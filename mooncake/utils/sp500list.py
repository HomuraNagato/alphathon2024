# ------------------------------------------------
# Get the list of tickers in the S&P500 for each year
# Used to initialize the stock list given the year
# ------------------------------------------------
import pandas as pd
import pyreadstat
from utils.utilities import convert_sas_date

sp500_file = 'sp500list/sp500cik.sas7bdat'
# Read the .sas7bdat file into a Pandas DataFrame
sp500, meta = pyreadstat.read_sas7bdat(sp500_file)
sp500.rename(columns={"TICKER": "ticker"}, inplace=True)

sp500
sp500["ym"] = sp500['DATE'].apply(lambda x: convert_sas_date(x, '%Y-%m'))

sp500_ym = sp500.groupby('ym')['ticker'].unique().reset_index()
sp500_ym.rename(columns={'ticker': 'tickers'}, inplace=True)

tickers = sp500_ym.query('ym == "2000-01"')['tickers'].values[0].tolist()
sp500_ym.to_csv("sp500_ym.csv")