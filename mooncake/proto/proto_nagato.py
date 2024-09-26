
import csv
from io import StringIO
import os
import pandas as pd
from pathlib import Path
import sys

sys.path.append(os.getcwd())

from llm.utils.yaml_editor import YamlEditor
from utils.utilities import create_path, inspect_df, hash_text, _open

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
  #check_10ks()
  #ten_ks_data_loader()
  text01 = "wonderful"
  text02 = "despair"

  #fname_cache = Path("portfolio_cache.yaml")
  fname_cache = "portfolio_cache.yaml"
  
  #if not fname_cache.is_file():
  #  fname_cache.touch()
  #portfolio_cache = _open(fname_cache) or {}
  portfolio_cache = YamlEditor(fname_cache)
  key = hash_text(text01, text02)
  print(portfolio_cache)
  portfolio_cache.update_key(key, "buy")
  print(portfolio_cache)
  portfolio_cache.save()
