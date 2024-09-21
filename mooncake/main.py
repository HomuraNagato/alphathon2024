# region imports
from AlgorithmImports import *
import pandas as pd
import os
from io import StringIO
from datetime import date
# endregion

class MoonCake(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 1, 1)
        self.set_cash(100000)
        self.add_equity("SPY", Resolution.DAILY)
        self.add_equity("AAPL", Resolution.DAILY)
        self.add_equity("NVDA", Resolution.DAILY)

        # self.portfolio_weights = pd.read_csv("portfolio_weights.csv")
        weights_string = self.object_store.read("mooncake/portfolio_weights.csv")
        weights_string = StringIO(weights_string)
        self.portfolio_weights = pd.read_csv(weights_string)

        # self.schedule.on(self.date_rules.month_start("SPY"),
        #                  self.time_rules.after_market_open("SPY"),
        #                  self.rebalance_portfolio)

    def first_trading_day_of_month(self, today: str) -> bool: 
        first_day_of_current_month = date(today.year, today.month, 1)
        today = today.strftime('%Y-%m-%d')
        trading_days = self.TradingCalendar.GetTradingDays(first_day_of_current_month, self.EndDate) 
        first_trading_day = next(day for index, day in enumerate(trading_days) if day.BusinessDay) 
        first_trading_day = first_trading_day.Date.date().strftime('%Y-%m-%d')
        self.Debug("Comparing " + str(today) + " to " + str(first_trading_day)) 
        # Compare datetime.date objects 
        return today == first_trading_day

    def on_data(self, data: Slice):
        if not self.portfolio.invested:
            # self.set_holdings("SPY", 0.33)
            # self.set_holdings("BND", 0.33)
            self.set_holdings("AAPL", 0)
            self.set_holdings("NVDA", 1)
    
        # Schedule rebalancing based on dates in the dataframe
        # for index, row in self.portfolio_weights.iterrows():
        self.today = self.Time
        # self.Debug("today year is: " + str(self.today.year) + " & month: " + str(self.today.month))
        # self.Debug("and the date is: " + str(date(self.today.year, self.today.month, 1)))
        if self.first_trading_day_of_month(self.today):
            self.Debug("today is the first trading day of the month: " + str(self.today))
            # rebalance the portfolio on these days
            self.schedule.on(
                self.date_rules.month_start("SPY"),
                self.time_rules.after_market_open("SPY"),
                self.rebalance_portfolio
            )
    
    # def rebalance_portfolio(self):
    #     if self.time >= datetime(2021, 1, 1):
    #         self.SetHoldings("AAPL", 1)
    #         self.SetHoldings("NVDA", 0)

    def rebalance_portfolio(self):
        today = self.Time.strftime('%Y-%m-%d') # re-initialize the today variable as it can get out of sync calling self.today
        self.Debug("rebalancing the portfolio on: " + str(today))
        # Find the row for the current date
        this_month_stocks = self.portfolio_weights.query('date == @today')
        self.Debug("this month stocks are: " + str(this_month_stocks))

        if len(this_month_stocks) > 0:
            # Set holdings based on the weights
            for index, row in this_month_stocks.iterrows():
                self.Debug("ticker is: " + str(row["ticker"]) + " and weight is: " + str(row["weight"]))
                # if ticker != 'date':
                self.SetHoldings(row["ticker"], row["weight"])
        

    