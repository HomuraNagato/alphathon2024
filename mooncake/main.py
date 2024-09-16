
from AlgorithmImports import *
import pandas as pd
import os

from sas_custom_data import SaSData

class UpgradedRedDolphin(QCAlgorithm):

    def initialize(self):
        #self.set_start_date(2020, 3, 12)
        self.set_start_date(2021, 1, 1)
        self.set_end_date(2022, 1, 1)
        self.set_cash(100000)
        self.symbols = []
        # To store SPY data
        #spy_symbol = self.add_equity("SPY", Resolution.Minute).Symbol

        #nvda_symbol = self.add_equity("NVDA").symbol
        #df = self.history(nvda_symbol, 360, Resolution.DAILY)
        # file_path = self.object_store.get_file_path("df_to_csv")
        # df.to_csv(file_path)   # File size: 32721 bytes
        # pd_df = pd.DataFrame(df)
        # pd_df.to_csv("data.csv")

        # save to local project
        # Define the file path within the project folder
        #file_path = os.path.join(os.getcwd(), "df_to_csv.csv")
        # file_path = os.path.join(project_directory, "df_to_csv.csv")

        # Save the DataFrame to the CSV file in the project folder
        # df.to_csv(file_path)
        # df.to_csv("data.csv")
        # df.to_csv("/data/data.csv")
        # df.to_csv("/mnf/data/data.csv")

        symbol_list = self.open_symbol_list()
        #symbol_list = ["NVDA", "AAPL", "COST"]  # for prototyping
        self.init_symbols = symbol_list.copy()

        for symbol in symbol_list:
            tmp = self.add_data(SaSData, symbol, Resolution.DAILY).symbol
            self.symbols.append(tmp)
        
            history = self.history(SaSData, symbol, 1000, Resolution.DAILY)
            self.debug(f"We have {len(history)} items from historical data request of {symbol}")

        self.portfolio_size = min(len(self.symbols), 500)  # sp500list ~ 1400 stocks

        self.log(f"we have a total of {len(self.symbols)} symbols in our S&P 500 universe")
        # TODO, on_data init portfolio needs to wait for warm_up to finish?
        #self.set_warm_up(1000)

    def open_symbol_list(self):
        fname_symbols = os.path.join(Globals.DataFolder, "sp500_symbols", "symbol_list" + ".txt")
        f = open(fname_symbols)
        symbols = [ line.strip() for line in f ]
        f.close()
        self.log(f"{len(symbols)}  symbols added to symbol list")
        return symbols

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
        self.log(f"invested? {self.portfolio.invested}")

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
    
    # def on_end_of_algorithm(self):
    #     # Convert the list of SPY data to a Pandas DataFrame
    #     df = pd.DataFrame(self.spy_data, columns=["Time", "SPY_Close_Price"])

    #     # Save the DataFrame as a CSV file
    #     df.to_csv("/data/SPY_data.csv", index=False)

    #     # Output a message in the log
    #     self.debug("SPY data has been saved as CSV.")
    
