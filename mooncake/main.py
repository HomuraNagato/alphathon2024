# region imports
from AlgorithmImports import *
import pandas as pd
import os
# endregion

class UpgradedRedDolphin(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 3, 12)
        self.set_cash(100000)
        self.add_equity("SPY", Resolution.MINUTE)
        self.add_equity("BND", Resolution.MINUTE)
        self.add_equity("AAPL", Resolution.MINUTE)
        self.add_equity("NVDA", Resolution.DAILY)

        # To store SPY data
        spy_symbol = self.add_equity("SPY", Resolution.Minute).Symbol
        self.spy_data = []

        nvda_symbol = self.add_equity("NVDA").symbol
        df = self.history(nvda_symbol, 360, Resolution.DAILY)
        # file_path = self.object_store.get_file_path("df_to_csv")
        # df.to_csv(file_path)   # File size: 32721 bytes
        # pd_df = pd.DataFrame(df)
        # pd_df.to_csv("data.csv")

        # save to local project
        # Define the file path within the project folder
        file_path = os.path.join(os.getcwd(), "df_to_csv.csv")
        # file_path = os.path.join(project_directory, "df_to_csv.csv")

        # Save the DataFrame to the CSV file in the project folder
        # df.to_csv(file_path)
        # df.to_csv("data.csv")
        # df.to_csv("/data/data.csv")
        # df.to_csv("/mnf/data/data.csv")



    def on_data(self, data: Slice):
        if not self.portfolio.invested:
            self.set_holdings("SPY", 0.33)
            self.set_holdings("BND", 0.33)
            self.set_holdings("AAPL", 0.33)
        
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
    
