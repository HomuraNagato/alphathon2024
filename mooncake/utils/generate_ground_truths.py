
import numpy as np
import os
import pandas as pd
import sys

sys.path.append(os.getcwd())
from mooncake.utils.utilities import create_path, inspect_df, _open

def load_data(fname):

    df = pd.read_csv(fname)
    df.columns = [ x.lower() for x in df.columns ]
    df["ticker"] = df["ticker"].str.replace("'", "")
    dt_format = "%Y-%m-%d"
    if "-" not in str(df.loc[0,"date"]):
        dt_format = "%Y%m%d"
    df["date"] = pd.to_datetime(df["date"], format=dt_format)

    return df


if __name__ == "__main__":

    # load 10ks and stock data
    # merge on sticker and date

    # determine ground truth as 10 day avg after 10ks
    # if higher, buy, else low

    fname_out = "mooncake/data/10ks/10ks_truths.csv"
    df_10ks = load_data("mooncake/data/10ks/df_10ks.csv")
    df_sp500 = load_data("mooncake/data/sp500list/sp500list.csv")
    df_sp500 = df_sp500.dropna(subset=["prc"])
    window_size = 10

    # calculate rolling window for sp500 for each group of ticker
    # then calculate truth based on current price and window price
    df_sp500.loc[:,"prc_rolling"] = df_sp500.loc[:,:].groupby("ticker")["prc"].rolling(window_size).mean().reset_index(0, drop=True)
    df_sp500.loc[:,"truth"] = np.where(df_sp500.loc[:,"prc"] <= df_sp500.loc[:,"prc_rolling"], "buy", "sell")
    df = pd.merge(df_10ks, df_sp500, on=["date", "ticker"], how="left")
    # TODO, appears some truths are NA? investigate cause; perhaps merge is within rolling window?
    df = df.dropna(subset=["truth"])
    # subset columns?

    df.to_csv(fname_out, index=False)
