
# overview

Using LLM's to build a portfolio that beats the S&P 500.

## prep

make sure mooncake/sp500list.csv exists
`python mooncake/utils/split_data.csv`
this will create a directory with all of the symbol data in `data/sp500_symbols/`

## test

should be able to run `lean backtest mooncake`
note, if include entire universe of symbols, might take > 15 min to load all of
the data.
