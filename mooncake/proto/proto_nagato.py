
import os
import pandas as pd
import sys

sys.path.append(os.getcwd())

from mooncake.utils.utilities import inspect_df

def check_symbol_open():
    fname_symbols = os.path.join(os.getcwd(), "data", "sp500_symbols", "symbol_list" + ".txt")
    f = open(fname_symbols)
    symbols = [ line.strip() for line in f ]
    f.close()

    print(f"{len(symbols)}  {symbols}")

def check_10ks():

  fname = "mooncake/sp500list/df_10ks.csv"
  df = pd.read_csv(fname)
  inspect_df(df)
  for idx, col in enumerate(df.columns):
    print(f"{idx} {col}")

if __name__ == "__main__":
 
  #check_symbol_open()
  check_10ks()
