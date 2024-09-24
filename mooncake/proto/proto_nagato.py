
import csv
from io import StringIO
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

  fname = "mooncake/data/sp500list/sp500list_10ks.csv"
  fname = "mooncake/data/merged/10ks_truths.csv"

  df = pd.read_csv(fname, sep="|")
  inspect_df(df)
  for idx, col in enumerate(df.columns):
    print(f"{idx} {col}")

def ten_ks_data_loader():

  fname = "mooncake/data/sp500list/sp500list_10ks.csv"
  f = open(fname)

  count = 0
  for line in f:
    data = line.split("|")

    print(f" {len(data)}  {data=}")
    count += 1
    if count == 0:
      continue

    
    if count > 3:
      break
    
if __name__ == "__main__":
 
  #check_symbol_open()
  check_10ks()
  #ten_ks_data_loader()
