
from AlgorithmImports import *
from datetime import date
from io import StringIO
import pandas as pd
import os
import random

from custom_data_loader import SaSData
from llm.models.message_preparatory import MessageTestEngine
# TODO, why can't import from utils.utilities??
from llm.utils.utilities import create_path, hash_text, inspect_df, _open
from llm.utils.yaml_editor import Checkpoint, YamlEditor


class MoonCake(QCAlgorithm):

    def initialize(self):

        self.set_start_date(2010, 1, 1)
        self.set_end_date(2012, 1, 1)
        self.set_cash(100000)
        self.symbols = []
        self.rebalance_list = []

        # constants
        self.col_openai = "openai_response"
        self.col_hash = "hashed_text"
        self.model_key = "model_v002"

        self.llm_config = _open(os.path.join(Globals.DataFolder, "configs", "config_sp500_10k.yaml"))
        self.portfolio_cache = YamlEditor(os.path.join(Globals.DataFolder, "portfolio_cache.yaml"))
        #self.llm_config = _open(os.getcwd() + "/mooncake/llm/configs/config_sp500_10k.yaml")

        #sp500_symbol_list = self.open_symbol_list("sp500_symbols")
        #ten_ks_symbol_list = self.open_symbol_list("10ks")
        #symbol_list = list(set(sp500_symbol_list) | set(ten_ks_symbol_list))
        symbol_list = ["NVDA", "AAPL", "COST", "SBUX"]  # for prototyping
        self.init_symbols = symbol_list.copy()
        self.add_equity("SPY", Resolution.DAILY)
        #self.add_equity("AAPL", Resolution.DAILY)
        #self.add_equity("NVDA", Resolution.DAILY)

        #self.add_symbols(symbol_list, "sp500", SaSData)
        self.add_symbols(symbol_list, "10ks", SaSData)
            
        self.portfolio_size = min(len(self.symbols), 500)  # sp500list ~ 1400 stocks

        self.log(f"we have a total of {len(self.symbols)} symbols in our S&P 500 universe")
        # TODO, on_data init portfolio needs to wait for warm_up to finish?
        #self.set_warm_up(1000)

        # self.portfolio_weights = pd.read_csv("portfolio_weights.csv")
        #weights_string = self.object_store.read("mooncake/portfolio_weights.csv")
        #weights_string = StringIO(weights_string)
        #self.portfolio_weights = pd.read_csv(weights_string)

        self.schedule.on(self.date_rules.month_start("SPY"),
                         self.time_rules.after_market_open("SPY"),
                         self.rebalance_portfolio)

    def open_symbol_list(self, pdir):
        fname_symbols = os.path.join(Globals.DataFolder, pdir, "symbol_list" + ".txt")
        f = open(fname_symbols)
        symbols = [ line.strip() for line in f ]
        f.close()
        self.log(f"{len(symbols)}  symbols added to symbol list")
        return symbols

    def add_symbols(self, symbol_list, name, custom_loader):
        for symbol in symbol_list:
            tmp = self.add_data(custom_loader, symbol, Resolution.DAILY).symbol
            self.symbols.append(tmp)
        
            history = self.history(custom_loader, symbol, 1000, Resolution.DAILY)
            self.debug(f"10ks: We have {len(history)} items from historical data request of {symbol}")

    def on_data(self, data: Slice):
        # add symbols on first appearance
        seen = set()
        for symbol in self.init_symbols:
            if data.contains_key(symbol):
                weight = round(1/self.portfolio_size, 3)
                self.log(f"purchasing {symbol} with weight {weight}")
                self.set_holdings(symbol, weight)
                seen.add(symbol)

        # remove symbols that have been added in this timeslice
        self.init_symbols = list(set(self.init_symbols) - seen)

        # create dataframe that can be used for llm request
        no_text = "No text available"
        for key, obj in data.items():
            if type(obj) == PythonData:
                item_1 = obj.ten_ks["item_1"]
                item_1a = obj.ten_ks["item_1a"]
                item_7a = obj.ten_ks["item_7a"]
            
                if (item_1 != no_text or item_1a != no_text or item_7a != no_text):
                    #self.log(f"data {obj.symbol.value}.  {item_1a}")
                    self.rebalance_list.append([ obj.symbol.value, item_1, item_1a, item_7a ])

        # Schedule rebalancing based on dates in the dataframe
        # for index, row in self.portfolio_weights.iterrows():
        self.today = self.Time
        # self.Debug("today year is: " + str(self.today.year) + " & month: " + str(self.today.month))
        # self.Debug("and the date is: " + str(date(self.today.year, self.today.month, 1)))
        if self.first_trading_day_of_month(self.today):
            self.Debug("today is the first trading day of the month: " + str(self.today))
            # rebalance the portfolio on these days
            #self.schedule.on(
            #    self.date_rules.month_start("SPY"),
            #    self.time_rules.after_market_open("SPY"),
            #    self.rebalance_portfolio
            #)
        # spy = self.add_equity("SPY").symbol
        # df = self.history(self.securities.keys, 360, Resolution.DAILY)
        # file_path = self.object_store.get_file_path("df_to_csv")
        # df.to_csv(file_path)   # File size: 32721 bytes
        
        # Store SPY data
        # if data.contains_key(self.spy_symbol) and data[self.spy_symbol] is not None:
        #     spy_price = data[self.spy_symbol].Close
        #     spy_time = self.time

        #     # Append the time and price to the list
        #     self.spy_data.append([spy_time, spy_price])

    def check_cache(self, df):
        # create a hash of the text to use as a key in hash file
        # if key exists, get result, otherwise cell is empty

        def row_hash(row):
            return hash_text(row["item_1"], row["item_1a"], row["item_7a"])

        def get_cache(row):
            return self.portfolio_cache.get(row[self.col_hash], "")

        choices = ["buy", "sell"]
        if df.shape[0] == 0:
            return df

        df[self.col_hash] = df.apply(row_hash, axis=1)
        df[self.col_openai] = df.apply(get_cache, axis=1)

        return df

    def request_llm(self, df):

        def set_cache(row):
            return self.portfolio_cache.update_key(row[self.col_hash], row[self.col_openai])

        if df.shape[0] == 0:
            return df

        # subset to entries that weren't in cache
        cached_idx = df.loc[:,self.col_openai] == ""
        df_tmp = df.loc[cached_idx,:]

        if df_tmp.shape[0] == 0:
            return df

        # make request
        self.log(f"requesting llm for {df_tmp.shape[0]} portfolio recommendations")
        message_engine = MessageTestEngine(self.llm_config)
        prompts, res = message_engine.solicitation_test(df_tmp, self.model_key)
        message_engine.update_df(df_tmp,
                                 self.col_openai,
                                 res)
        chkpnt.remove()

        # update df with openai responses
        df.loc[cached_idx,self.col_openai] = df_tmp.loc[cached_idx,self.col_openai]
        self.log(f"cache df {df_tmp}")

        # update cache with openai responses (overwrite existing values with same)
        df.apply(set_cache, axis=1)
        self.portfolio_cache.save()

        return df

    def first_trading_day_of_month(self, today: str) -> bool: 
        first_day_of_current_month = date(today.year, today.month, 1)
        today = today.strftime('%Y-%m-%d')
        trading_days = self.TradingCalendar.GetTradingDays(first_day_of_current_month, self.EndDate) 
        first_trading_day = next(day for index, day in enumerate(trading_days) if day.BusinessDay) 
        first_trading_day = first_trading_day.Date.date().strftime('%Y-%m-%d')
        #self.Debug("Comparing " + str(today) + " to " + str(first_trading_day)) 
        # Compare datetime.date objects 
        return today == first_trading_day

    def rebalance_portfolio(self):
        today = self.Time.strftime('%Y-%m-%d') # re-initialize the today variable as it can get out of sync calling self.today
        self.Debug(f"rebalancing the portfolio on: {today}")
        # Find the row for the current date
        #this_month_stocks = self.portfolio_weights.query('date == @today')
        #self.Debug("this month stocks are: " + str(this_month_stocks))

        df_rebalance = pd.DataFrame(self.rebalance_list, columns=["ticker", "item_1", "item_1a", "item_7a"])
        #self.log(f"df_rebalance shape {df_rebalance.shape}")

        df_rebalance = self.check_cache(df_rebalance)
        df_rebalance = self.request_llm(df_rebalance)
        #records = df_rebalance.to_dict(orient="records")

        # TODO, make rebalance_portfolio method to use recommendations as parameter in weight allocation
        # Set holdings based on the weights
        #for row in records:
        #    self.log(f"llm recommendation for {row['ticker']} is to {row['openai_response']}")
            #self.Debug("ticker is: " + str(row["ticker"]) + " and weight is: " + str(row["weight"]))
            # if ticker != 'date':
            #self.SetHoldings(row["ticker"], row["weight"])

        # clear list for next rebalancing
        self.rebalance_list = []
