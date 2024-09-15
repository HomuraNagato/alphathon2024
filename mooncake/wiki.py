from AlgorithmImports import *
import pandas as pd

class UpgradedRedDolphin(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2020, 3, 12)
        self.set_cash(100000)
        # Add Quandl data
        self.add_data(Quandl, "WIKI/AAPL", Resolution.Daily)
        # Add SPY data
        self.spy_symbol = self.add_equity("SPY", Resolution.Minute).Symbol
        self.spy_data = []
        

    def on_data(self, data):
        # Access Quandl data
        if data.contains_key("WIKI/AAPL"):
            quandl_data = data["WIKI/AAPL"]
            self.debug(f"Quandl Data: {quandl_data.Value}")
                # Check if SPY data is available in the current slice
        
        if data.contains_key(self.spy_symbol):
            spy_price = data[self.spy_symbol].Close
            spy_time = self.time

            # Append the time and price to the list
            self.spy_data.append([spy_time, spy_price])
    
    def on_end_of_algorithm(self):
        # Convert the list of SPY data to a Pandas DataFrame
        df = pd.DataFrame(self.spy_data, columns=["Time", "SPY_Close_Price"])

        # Save the DataFrame as a CSV file
        df.to_csv("SPY_data.csv", index=False)

        # Output a message in the log
        self.debug("SPY data has been saved as CSV.")
