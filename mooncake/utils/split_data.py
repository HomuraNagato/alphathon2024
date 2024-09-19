
import os
import pandas as pd
from pathlib import Path
import sys

sys.path.append(os.getcwd())

from mooncake.utils.utilities import create_path

def split_sp500():

    pdir = Path("./data/sp500_symbols/")
    fname_data = "./mooncake/sp500list/sp500list.csv"  # Replace with your desired CSV filename
    fname_symbols = (pdir / "symbol_list").with_suffix(".txt")
    create_path(fname_symbols)
    f = open(fname_symbols, "w")
    count = 0

    df = pd.read_csv(fname_data)
    df["TICKER"] = df["TICKER"].str.replace("'", "")

    symbols = df["TICKER"].unique()
    symbols = sorted([ str(x) for x in symbols ])
    print(f"will create {len(symbols)} individual symbol data files")

    for symbol in symbols:
        f.write(symbol + "\n")
        df_tmp = df.loc[df["TICKER"] == symbol]
        fout = (pdir / symbol.lower()).with_suffix(".csv")
        df_tmp.to_csv(fout, index=False, header=False)
        count += 1

    f.close()
    print(f"saved symbol list to {fname_symbols}")
    print(f"created {count} individual symbol data files")

def split_10ks():

    pdir = Path("./data/10ks/")
    fname_data = "./mooncake/sp500list/df_10ks.csv"  # Replace with your desired CSV filename
    fname_symbols = (pdir / "symbol_list").with_suffix(".txt")
    create_path(fname_symbols)
    f = open(fname_symbols, "w")
    count = 0

    df = pd.read_csv(fname_data)

    symbols = df["TICKER"].unique()
    symbols = sorted([ str(x) for x in symbols ])
    print(f"will create {len(symbols)} individual symbol data files")

    for symbol in symbols:
        f.write(symbol + "\n")
        df_tmp = df.loc[df["TICKER"] == symbol]
        fout = (pdir / symbol.lower()).with_suffix(".csv")
        df_tmp.to_csv(fout, index=False, header=False)
        count += 1

    f.close()
    print(f"created {count} individual 10ks data files")


if __name__ == "__main__":

    #split_sp500()
    split_10ks()
