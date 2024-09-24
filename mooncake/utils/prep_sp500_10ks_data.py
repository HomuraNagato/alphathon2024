
import argparse
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys

sys.path.append(os.getcwd())

from mooncake.utils.utilities import create_path, inspect_df, _open


def initialise():
    parse = argparse.ArgumentParser(
        description="prep sp500 and 10k data into directory with separate symbol data; including 'ground truth'",
        epilog="example: python mooncake/utils/prep_sp500_10ks_data.py")
    parse.add_argument("--fname_10ks",
                       required=True,
                       help="path to initial 10ks data")
    parse.add_argument("--fname_sp500",
                       required=True,
                       help="path to initial sp500 data")
    parse.add_argument("--fname_out",
                       required=True,
                       help="save location for merged dataframe")
    parse.add_argument("--out_dir",
                       required=True,
                       help="directory to (create and ) save individual symbol data usable by quantconnect")
    parse.add_argument("--how",
                       nargs="?",
                       default="left",
                       help="merge 10ks (dfA) with sp500 (dfB) whether left or right")
    parse.add_argument("--window_size",
                       nargs="?",
                       type=int,
                       default=10,
                       help="how many days to 'look-ahead' for generating llm signal")
    args = parse.parse_args()

    return args

def load_data(fname):

    df = pd.read_csv(fname)
    df.columns = [ x.lower() for x in df.columns ]
    # date and DATE columns ...
    df = df.loc[:,~df.columns.duplicated()]
    dt_format = "%Y-%m-%d"
    if "-" not in str(df.loc[0,"date"]):
        dt_format = "%Y%m%d"
    df["date"] = pd.to_datetime(df["date"], format=dt_format)

    return df


def generate_ground_truths(fname_10ks, fname_sp500, fname_out, window_size=10, how="left"):
    # 1.   calculate rolling average of price
    # 2a.  merge both dataframes; will included 'today' price and 'future' price
    # 2b.  'future' >= 'today' ? buy : sell
    # 3.   choose direction for merge and output
    # TODO more nuanced than boolean?
    # TODO consider if this is too simplistic for llm ground truth

    # load 10ks and stock data
    prc_col = "prc_adj"
    df_10ks = load_data(fname_10ks)
    df_10ks = df_10ks.replace(r'\n', '', regex=True)
    # drop (or spline?) missing data
    df_sp500 = load_data(fname_sp500)
    df_sp500 = df_sp500.dropna(subset=[prc_col])

    # calculate rolling window for sp500 for each group of ticker
    # then calculate truth based on current price and window price
    # include magnitude, the percent of increase/decrease truth = prc_rolling/prc -> bin
    # 
    df_sp500.loc[:,"prc_rolling"] = df_sp500.loc[:,:].groupby("ticker")[prc_col].rolling(window_size).mean().reset_index(0, drop=True)
    df_sp500.loc[:,"truth"] = np.where(df_sp500.loc[:,prc_col] <= df_sp500.loc[:,"prc_rolling"], "buy", "sell")

    # how=left   merge 10ks <- sp500
    # how=right  merge 10ks -> sp500
    df = pd.merge(df_10ks, df_sp500, on=["date", "ticker"], how=how)
    
    # TODO  left  appears some truths are NA? investigate cause; perhaps merge is within rolling window?
    # TODO  right  df.shape > df_sp500.shape, how??
    df = df.dropna(subset=["truth"])
    # subset columns?
    breakpoint()
    df.to_csv(fname_out, sep="|", index=False)


def split_data(out_dir, fname_data):

    out_dir = Path(out_dir)
    fname_symbols = (out_dir / "symbol_list").with_suffix(".txt")
    create_path(fname_symbols)
    f = open(fname_symbols, "w")
    count = 0

    df = pd.read_csv(fname_data, sep="|")
    df["ticker"] = df["ticker"].str.replace("'", "")

    symbols = df["ticker"].unique()
    symbols = sorted([ str(x) for x in symbols ])
    print(f"will create {len(symbols)} individual symbol data files")

    for symbol in symbols:
        f.write(symbol + "\n")
        df_tmp = df.loc[df["ticker"] == symbol]
        fout = (out_dir / symbol.lower()).with_suffix(".csv")
        df_tmp.to_csv(fout, sep="|", index=False, header=False)
        count += 1

    f.close()
    print(f"saved symbol list to {fname_symbols}")
    print(f"created {count} individual data files stored in {str(out_dir)}")

if __name__ == "__main__":

    args = initialise()

    # rolling average of price, merge into one of the dataframes
    generate_ground_truths(args.fname_10ks, args.fname_sp500, args.fname_out,
                           window_size=args.window_size, how=args.how)
    
    # split data into separate symbols (without header) to use with quantconnect
    split_data(args.out_dir, args.fname_out)


