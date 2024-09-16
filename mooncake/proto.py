
import os
import sys

sys.path.append(os.getcwd())

def check_symbol_open():
    fname_symbols = os.path.join(os.getcwd(), "data", "sp500_symbols", "symbol_list" + ".txt")
    f = open(fname_symbols)
    symbols = [ line.strip() for line in f ]
    f.close()

    print(f"{len(symbols)}  {symbols}")

if __name__ == "__main__":

    check_symbol_open()
