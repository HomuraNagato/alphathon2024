
import logging
import json
import pandas as pd
import pathlib
import sys
import toml
import yaml

def _open(fname, sep=",", types_dict=None):
    """
    use the file extension to try and open the passed in file name

    txt is treated the same as csv
    csv's can be either '|' or ',' delimited
    perhaps might want to remove the first line peak and simply require an argument?
    """

    res = None
    log_util.info(f"loading {fname}")

    if isinstance(fname, str):
        fname = pathlib.Path(fname)

    dtype = fname.suffix[1:]

    def generic_open(fname, func, rw):
        with open(fname, rw) as f:
            result = func(f)

        return result

    if dtype == 'json':
        if os.stat(fname).st_size == 0:
            res = {}  # json can't load from empty file
        else:
            res = generic_open(fname, json.load, 'r')

    elif dtype =='jsonl':
        res = []
        f = open(fname, 'r')
        for line in f:
            res.append(json.loads(line))
        f.close()

    elif dtype == 'yaml':
        res = generic_open(fname, yaml.safe_load, 'r')

    elif (dtype == 'csv') or (dtype == 'txt'):
        res = pd.read_csv(fname, sep=sep, dtype=types_dict)

    elif dtype == 'pkl':
        res = generic_open(fname, pickle.load, 'rb')

    elif dtype == 'ftr':
        res = pd.read_feather(fname)

    elif dtype =='toml':
        res = generic_open(fname, toml.load, 'r')

    else:
        log.error("please provide a support data type {.json, .yaml, .csv, .txt, .pkl, .ftr}")
        exit()

    return res

def create_path(path):
    # convert to Path if necessary
    # create parent dir if necessary
    if not isinstance(path, pathlib.PurePath):
        path = pathlib.Path(path)
    path_way = path.parent if path.is_file() else path
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

def get_logger(logname=__name__, loglevel=logging.INFO, verbose=None):

    # if logger already made, return it
    if logname in logging.Logger.manager.loggerDict:
        return logging.getLogger(logname)

    format = '%(asctime)s %(thread)s %(name)s %(levelname)-8s %(message)s'
    datefmt = '%y.%m.%d %H:%M:%S'
    handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(format=format, level=loglevel, datefmt=datefmt, handlers=handlers)
    return logging.getLogger(logname)

def inspect_df(df, description="", log=None, cols=None, idx_start=0, idx_end=5):
    """
    helper function to simplify printing views of a df to console
    """
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    log = log_util if not log else log

    if not cols:
        cols = df.columns
    else:
        cols = [ c for c in cols if c in df.columns ]

    idx_range = df.index[idx_start:idx_end] # to work with non-int indices

    log.info(f"{description} ({df.shape})\n{df.loc[idx_range,cols]}")


def timerfunc(f_py=None, logname=None, logstart=False, verbose=False):
    """
    A timer decorator. With optional logging
    Adding a logname will now save to a file
    To also print to console, include both logname and verbose=True
    """
    assert callable(f_py) or f_py == None

    def _decorator(func):
        @functools.wraps(func)
        def function_timer(*args, **kwargs):
            """
            A nested function for timing other functions
            """
            log = get_logger(logname)
            start = time()
            start_msg = "init {func} ".format(func=func.__name__)
            if logstart:
                log.info(start_msg)
            res = func(*args, **kwargs)
            end = time()
            runtime = round(end - start, 4)
            end_msg = "The runtime for {logname}-{func} took {time} seconds to complete".format(
                logname=logname,
                func=func.__name__,
                time=runtime)
            log.info(end_msg)
            return res

        return function_timer

    return _decorator(f_py) if callable(f_py) else _decorator

#def reverse_key_single_level(d):
# given a dictionary where all keys are only str or numeric, reverse the dictionary
    
log_util = get_logger('util')
