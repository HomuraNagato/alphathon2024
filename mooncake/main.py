
from AlgorithmImports import *
from datetime import date
from io import StringIO
import pandas as pd
import os
import random
import numpy as np
from scipy.optimize import minimize

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
        self.current_portfolio = set()

        # constants
        self.col_openai = "openai_response"
        self.col_hash = "hashed_text"
        self.model_key = "model_v002"

        # self.llm_config = _open(os.path.join(Globals.DataFolder, "configs", "config_sp500_10k.yaml"))
        # self.llm_config = _open(os.getcwd() + "/mooncake/llm/configs/config_sp500_10k.yaml")
        self.llm_config = self.object_store.read("mooncake/configs/config_sp500_10k.json")
        self.portfolio_cache = YamlEditor("portfolio_cache.yaml")
        # exit()

        #sp500_symbol_list = self.open_symbol_list("sp500_symbols")
        #ten_ks_symbol_list = self.open_symbol_list("10ks")
        #symbol_list = list(set(sp500_symbol_list) | set(ten_ks_symbol_list))
        symbol_list = ["NVDA", "AAPL", "COST", "SBUX"]  # for prototyping
        self.init_symbols = symbol_list.copy()
        self.sp500_symbols = symbol_list.copy()
        self.add_equity("SPY", Resolution.DAILY)
        # self.add_equity("SBUX", Resolution.DAILY)
        # self.sbux = self.add_equity("SBUX", Resolution.Daily).Symbol

        self.add_symbols(symbol_list, "sp500", SaSData)
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
            self.log(f"adding symbol {str(symbol)} to add_data")
            if name == "10ks":
                tmp = self.add_data(custom_loader, symbol, Resolution.DAILY).symbol
            else:
                tmp = self.add_equity(symbol, Resolution.Daily).Symbol
            
            self.log(f"the resulting data is {str(tmp)}")
            self.symbols.append(tmp)
        
            history = self.history(custom_loader, tmp, 1000, Resolution.DAILY)
            self.log(f"the resulting data history is {str(history)}")
            self.log(f"10ks: We have {len(history)} items from historical data request of {symbol}")

    def on_data(self, data: Slice):
        # add symbols on first appearance
        seen = set()
        for symbol in self.init_symbols:
            if data.contains_key(symbol):
                weight = round(1/self.portfolio_size, 3)
                self.log(f"purchasing {symbol} with weight {weight}")
                self.set_holdings(symbol, weight)
                seen.add(symbol)
                self.current_portfolio.add(symbol)

        # remove symbols that have been added in this timeslice
        self.init_symbols = list(set(self.init_symbols) - seen)
        # exit()

        # create dataframe that can be used for llm request
        no_text = "No text available"
        for key, obj in data.items():
            # self.log("current obj is: " + str(obj))
            if type(obj) == PythonData:
                item_1 = obj.ten_ks["item_1"]
                item_1a = obj.ten_ks["item_1a"]
                item_7a = obj.ten_ks["item_7a"]
                position = obj.ten_ks["position"]
                self.log("position to take is: " + str(position))
            
                if (item_1 != no_text or item_1a != no_text or item_7a != no_text):
                    #self.log(f"data {obj.symbol.value}.  {item_1a}")
                    self.rebalance_list.append([ obj.symbol.value, item_1, item_1a, item_7a, position ])

        # Schedule rebalancing based on dates in the dataframe
        # for index, row in self.portfolio_weights.iterrows():
        self.today = self.Time
        # self.Debug("today year is: " + str(self.today.year) + " & month: " + str(self.today.month))
        # self.Debug("and the date is: " + str(date(self.today.year, self.today.month, 1)))
        # if self.first_trading_day_of_month(self.today):
        #    self.Debug("today is the first trading day of the month: " + str(self.today))
            # rebalance the portfolio on these days
            #self.schedule.on(
            #    self.date_rules.month_start("SPY"),
            #    self.time_rules.after_market_open("SPY"),
            #    self.rebalance_portfolio
            #)

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

    def get_stock_history(self, ticker: str) -> pd.DataFrame:
        # Request the stock history for the given ticker
        stock_history = self.History([ticker], 30, Resolution.Daily)
        # Check if the stock history is not empty
        if not stock_history.empty:
            # Convert the history object to a DataFrame and reset the index
            stock_history_df = stock_history.loc[ticker].reset_index()
            # Select only the relevant columns (date and close price)
            stock_history_df = stock_history_df[['time', 'close']]
            # Rename columns for clarity
            stock_history_df.rename(columns={'time': 'date', 'close': 'price'}, inplace=True)
            # Add the ticker column
            stock_history_df['ticker'] = ticker
            # Display the resulting DataFrame
            self.log(f"Stock history for {ticker}:\n{stock_history_df}")
            return stock_history_df

    # Function to calculate portfolio returns and volatility
    def portfolio_performance(self, weights, mean_returns, cov_matrix):
        returns = np.dot(weights, mean_returns)
        std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return std_dev, returns

    # Objective function to minimize (Here we focus on minimizing variance)
    def minimize_variance(self, weights, mean_returns, cov_matrix):
        return self.portfolio_performance(weights, mean_returns, cov_matrix)[0]

    def calculate_portfolio_weights(self, stock_histories: pd.DataFrame) -> pd.DataFrame:
        price_table = stock_histories.pivot_table(values='price', index='date', columns='ticker')
        returns = price_table.pct_change().dropna()
        annual_returns = returns.mean() * 252
        self.log(f"annual returns are: {annual_returns}")
        annual_covariance = returns.cov() * 252
        # Number of assets
        num_assets = len(annual_returns)
        # Constraints (the sum of weights is 1)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        # Boundaries for weights
        bounds = tuple((0, 1) for asset in range(num_assets))
        # Initial guess (equal distribution)
        init_guess = num_assets * [1. / num_assets,]
        # Minimize variance
        optimal_var = minimize(self.minimize_variance, init_guess, args=(annual_returns, annual_covariance), method='SLSQP', bounds=bounds, constraints=constraints)
        # Get the optimal weights
        optimal_weights = optimal_var.x
        list_weights = [float(weight) for weight in optimal_weights]
        new_portfolio_weights = pd.DataFrame({"ticker": annual_returns.reset_index()["ticker"],
                                              "weight": list_weights})
        self.log(f"New portfolio weights: {new_portfolio_weights}")
        return new_portfolio_weights

    def rebalance_portfolio(self):
        today = self.Time.strftime('%Y-%m-%d') # re-initialize the today variable as it can get out of sync calling self.today
        self.log(f"rebalancing the portfolio on: {today}")
        # Find the row for the current date
        #this_month_stocks = self.portfolio_weights.query('date == @today')
        #self.Debug("this month stocks are: " + str(this_month_stocks))

        df_rebalance = pd.DataFrame(self.rebalance_list, columns=["ticker", "item_1", "item_1a", "item_7a", "position"])
        #self.log(f"df_rebalance shape {df_rebalance.shape}")

        # TODO: As of Sept 26th - Data will be added to the self.rebalance_list on each day,
        # when rebalance portfolio runs at the start of each month, it will have accumulated the buy and sell
        # signals, can subset the df_rebalance to the buys to do the portfolio rebalancing
        df_rebalance = self.check_cache(df_rebalance)
        # df_rebalance = self.request_llm(df_rebalance)
        self.log(f"df_rebalance is {str(df_rebalance)}")
        records = df_rebalance.to_dict(orient="records")

        # TODO, make rebalance_portfolio method to use recommendations as parameter in weight allocation
        # Set holdings based on the weights
        self.log(f"portfolio tickers include: {str(self.current_portfolio)}")
        stock_histories = pd.DataFrame()
        # add and remove stocks to rebalance to the portfolio
        # for row in records:
        df_rebalance = df_rebalance.groupby("ticker").tail(1)
        for index, row in df_rebalance.iterrows():
            self.log(f"llm recommendation for {str(row['ticker'])} is to {str(row['position'])}")
            self.log(f"current portfolio is: {self.current_portfolio}")
            if row['position'] == 'buy':
                self.current_portfolio.add(str(row['ticker']))
            elif row['position'] == 'sell':
                self.log(f"removeing from the portfolio: {str(row['ticker'])}")
                self.current_portfolio.discard(str(row['ticker']))
        #
        for ticker in self.current_portfolio:
            # stock_history = self.history(row['ticker'], 1000, Resolution.DAILY)
            # stock_history_df = pd.DataFrame({"price": [stock_history['close']]})
            this_stock_history = self.get_stock_history(ticker)
            stock_histories = pd.concat([stock_histories, this_stock_history], ignore_index=True)
            # self.log(f"the stock's history is: {stock_history_df}")# with mean: {price.close.mean()}")
            # self.log(f"ticker is: {str(row["ticker"])} and weight is: {str(row["weight"]))
            # self.SetHoldings(row["ticker"], row["weight"])
        
        # clear list for next rebalancing
        # self.rebalance_list = []
        # calculate returns
        if len(stock_histories) > 0:
            self.log(f"stock_histories is: {stock_histories}")
            self.log(f"with columns is: {stock_histories.columns}")
            new_portfolio_weights = self.calculate_portfolio_weights(stock_histories)
            sp500_df = pd.DataFrame({"ticker": self.sp500_symbols})
            portfolio_df = sp500_df.merge(new_portfolio_weights, how="left", on="ticker")
            portfolio_df = portfolio_df.fillna(0)
            self.log(f"portfolio_df is {portfolio_df}")
            for i, row in portfolio_df.iterrows():
                self.SetHoldings(row["ticker"], row["weight"])