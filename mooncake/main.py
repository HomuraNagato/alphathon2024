
from AlgorithmImports import *
import pandas as pd
import os

from custom_data_loader import SaSData
from llm.models.message_preparatory import MessageTestEngine
from llm.utils.utilities import create_path, inspect_df, _open
from llm.utils.yaml_editor import Checkpoint


class UpgradedRedDolphin(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2010, 1, 1)
        self.set_end_date(2012, 1, 1)
        self.set_cash(100000)
        self.symbols = []

        self.llm_config = _open(os.path.join(Globals.DataFolder, "configs", "config_sp500_10k.yaml"))
        #self.llm_config = _open(os.getcwd() + "/mooncake/llm/configs/config_sp500_10k.yaml")

        #sp500_symbol_list = self.open_symbol_list("sp500_symbols")
        #ten_ks_symbol_list = self.open_symbol_list("10ks")
        #symbol_list = list(set(sp500_symbol_list) | set(ten_ks_symbol_list))
        symbol_list = ["NVDA", "AAPL", "COST", "SBUX"]  # for prototyping
        self.init_symbols = symbol_list.copy()

        self.add_symbols(symbol_list, "sp500", SaSData)
        #self.add_symbols(symbol_list, "10ks", TenKData)
            
        self.portfolio_size = min(len(self.symbols), 500)  # sp500list ~ 1400 stocks

        self.log(f"we have a total of {len(self.symbols)} symbols in our S&P 500 universe")
        # TODO, on_data init portfolio needs to wait for warm_up to finish?
        #self.set_warm_up(1000)

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
        rebalance_list = []
        no_text = "No text available"
        for key, obj in data.items():
            item_1 = obj.ten_ks["item_1"]
            item_1a = obj.ten_ks["item_1a"]
            item_7a = obj.ten_ks["item_7a"]
            
            if (item_1 != no_text or item_1a != no_text or item_7a != no_text):
                #self.log(f"data {obj.symbol.value}.  {item_1a}")
                rebalance_list.append([ obj.symbol.value, item_1, item_1a, item_7a ])
        # TODO
        #if df_cache.exists:
        #    return pd.read_csv()
        df_rebalance = pd.DataFrame(rebalance_list, columns=["ticker", "item_1", "item_1a", "item_7a"])
        #self.log(f"df_rebalance shape {df_rebalance.shape}")

        records = self.request_llm(df_rebalance)
        
        # TODO, make rebalance_portfolio method to use recommendations as parameter in weight allocation
        for row in records:
            self.log(f"llm recommendation for {row['ticker']} is to {row['openai_response']}")

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

    def request_llm(self, df):

        model_key = "model_v002"
        response_col = "openai_response"
        records = []
        chkpnt = Checkpoint()

        if df.shape[0] == 0:
            return records

        # make request
        self.log(f"requesting llm for {df.shape[0]} portfolio recommendations")
        message_engine = MessageTestEngine(self.llm_config)
        prompts, res = message_engine.solicitation_test(df, model_key)
        message_engine.update_df(df,
                                 response_col,
                                 res)
        records = df.to_dict(orient="records")
        chkpnt.remove()

        return records
    
    # def on_end_of_algorithm(self):
    #     # Convert the list of SPY data to a Pandas DataFrame
    #     df = pd.DataFrame(self.spy_data, columns=["Time", "SPY_Close_Price"])

    #     # Save the DataFrame as a CSV file
    #     df.to_csv("/data/SPY_data.csv", index=False)

    #     # Output a message in the log
    #     self.debug("SPY data has been saved as CSV.")
    
