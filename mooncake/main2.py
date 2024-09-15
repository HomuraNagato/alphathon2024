from AlgorithmImports import *
import pandas as pd
from IPython.display import display

# Simulate part of the algorithm in the notebook environment
class UpgradedRedDolphin(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2020, 3, 12)
        self.set_cash(100000)
        
        # Define symbols
        self.btc_symbol = self.add_crypto("BTCUSD", Resolution.Daily).Symbol
        self.eth_symbol = self.add_crypto("ETHUSD", Resolution.Daily).Symbol

    def print_data(self):
        # Define time range for history request
        start_time = self.time - timedelta(days=3)
        end_time = self.time

        # Request historical data
        trade_bars_df = self.history(TradeBar, self.btc_symbol, start_time, end_time, Resolution.Daily)
        quote_bars_df = self.history(QuoteBar, self.btc_symbol, start_time, end_time, Resolution.Minute)
        ticks_df = self.history(Tick, self.eth_symbol, start_time, end_time, Resolution.Tick)
        combined_df = self.history(self.btc_symbol, start_time, end_time, Resolution.Hour)  # Includes trade and quote data

        # Print DataFrames using display for Jupyter Notebook
        print("Trade Bars DataFrame:")
        display(trade_bars_df.head())

        print("\nQuote Bars DataFrame:")
        display(quote_bars_df.head())

        print("\nTicks DataFrame:")
        display(ticks_df.head())

        print("\nCombined Trade and Quote Data (Resolution: Hour):")
        display(combined_df.head())

# Instantiate the class
algo = UpgradedRedDolphin()

# Set the necessary variables like time to simulate the QuantConnect environment
# algo.time = pd.Timestamp('2020-03-15')

# Simulate the initialize method to set up symbols
algo.initialize()

# Manually call the print_data method
algo.print_data()
