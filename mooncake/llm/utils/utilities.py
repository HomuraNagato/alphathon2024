
from datetime import datetime, timedelta
import hashlib
import json
import logging
import pandas as pd
import pathlib
import re
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

def hash_text(*texts):

    text = " ".join(texts)
    hash_object = hashlib.sha256()
    # Update the hash object with the text
    hash_object.update(text.encode())
    # Get the hexadecimal representation of the hash
    hashed_text = hash_object.hexdigest()

    return hashed_text

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


"""
Function to extract the items text in 10K and 10Q files
form_style may be either '10-K' or '10-Q'
"""
def extract_text_from_10x(file_name: str, form_style: str, keywords: list, sp500_ciks: pd.DataFrame, sequence_length: int = 2) -> pd.DataFrame:
    with open(file_name, 'r') as file:
        content = file.read()
    # Extract the ticker (CIK is often the closest identifier for this context)
    cik_match = re.search(r'CENTRAL INDEX KEY:\s+(\d+)', content)
    cik = cik_match.group(1) if cik_match else 'Unknown'
    # Company name
    company_name_match = re.search(r"COMPANY CONFORMED NAME:\s+([^\n]+)", content)
    company_name = company_name_match.group(1) if company_name_match else 'Unknown'
    # Extract the date (Filed as of date)
    date_match = re.search(r'FILED AS OF DATE:\s+(\d{8})', content)
    date = date_match.group(1) if date_match else 'Unknown'
    # exit early if cik is not in the sp500 list
    if len(sp500_ciks.query("cik == @cik")) == 0:
        data = {
            'cik': [cik],
            'company_name': [company_name],
            'date': [date],
            'form': "10K",
            'item_1': ["Skip"],
            'item_1A': ["Skip"],
            'item_7A': ["Skip"],
        }
        return pd.DataFrame(data)
    #
    if form_style == "10-K":
        item_1 = item_search(r"(Item 1)(.*?)(Item 1A)(.*?)", content)
        # item_1
        item_1A = item_search(r"(Item 1A)(.*?)(Item 1B)", content)
        # item_1A
        item_7A = item_search(r"(Item 7a\.)(.*?)(Item 8\.)", content)
        # item_7A
        item_1_cleaned = clean_text(item_1, keywords, sequence_length)
        # item_1_cleaned
        item_1A_cleaned = clean_text(item_1A, keywords, sequence_length)
        # item_1A_cleaned
        item_7A_cleaned = clean_text(item_7A, keywords, sequence_length)
        # item_7A_cleaned
        #
        data = {
            'cik': [cik],
            'company_name': [company_name],
            'date': [date],
            'form': "10K",
            'item_1': [item_1_cleaned],
            'item_1A': [item_1A_cleaned],
            'item_7A': [item_7A_cleaned],
        }
    elif form_style == "10-Q":
        item_1A = item_search("(ITEM 1A|Item 1A)(.*?)(ITEM 1B|Item 1B|2 Unregistered|2. Unregistered)", content)
        # item_1A
        item_2 = item_search("(ITEM 2|Item 2|2 Unregistered|2. Unregistered)(.*?)(ITEM 3|Item 3|3 Defaults|3. Defaults)", content)
        # item_2
        item_5 = item_search("(ITEM 5|Item 5|5 Other|5. Other)(.*?)(ITEM 6|Item 6|6 Exhibits|6. Exhibits)", content)
        # item_5
        item_1A_cleaned = clean_text(item_1, keywords, sequence_length)
        # item_1_cleaned
        item_2_cleaned = clean_text(item_2, keywords, sequence_length)
        # item_1A_cleaned
        item_5_cleaned = clean_text(item_5, keywords, sequence_length)
        # item_7A_cleaned
        data = {
            'cik': [cik],
            'company_name': [company_name],
            'date': [date],
            'form': ['10Q'],
            'item_1A': [item_1A_cleaned],
            'item_2': [item_2_cleaned],
            'item_5': [item_5_cleaned]
        }
    else:
        print("Please choose an appropriate file type")
        data = {'cik': [0000000000]}
    return pd.DataFrame(data)

"""
Extract text that was found from the regex
And return the longest matched passage
"""
def item_search(regex: str, content: str) -> str:
    item_matches = re.findall(regex, content, flags=re.DOTALL | re.IGNORECASE)
    # Find the match with the longest content
    longest_match = ''
    max_length = 0
    for match in item_matches:
        # Check the length of the second item in the tuple (the actual content)
        if len(match[1]) > max_length:
            max_length = len(match[1])
            longest_match = ''.join(match)
    # item = item_match[0].group(0).strip() if item_match else 'No text available'
    return longest_match if len(longest_match) > 0 else 'No text available'

# ------------------------------------------------
# Align date columns in preparation of merge
# ------------------------------------------------
def convert_sas_date(serial_date: float, date_format: str) -> str:
    # Excel origin date
    excel_origin = datetime(1960, 1, 1)
    # Calculate the date by adding the number of days to the origin
    target_date = excel_origin + timedelta(days=int(serial_date))
    # Format the date based on the given format
    return target_date.strftime(date_format)

def convert_10ks_date(date: str, date_format: str) -> str:
    # Parse the date string into a datetime object assuming the format is 'YYYYMMDD'
    parsed_date = datetime.strptime(date, '%Y%m%d')
    # Return the formatted date string as 'YYYY-MM-DD'
    return parsed_date.strftime(date_format)

"""
Split the text into an array
"""
def clean_and_split_text(text: str):
    # Remove 'Table of Contents' and any preceding numbers
    text = re.sub(r"^[A-Z\s]+\n", "\n", text, flags=re.MULTILINE)
    paragraphs = text.split("ble of Content") # sometimes Table is split in to Table or Ta ble
    if len(paragraphs) < 2:
    # cleaned_text = re.sub(r"\d+\s*\nTable of Contents\s*\n", "", text)
    # Remove company name in capital letters (assumed to be a line of uppercase words)
        paragraphs = text.split('\n\n')
    # Filter out empty paragraphs
    paragraphs = [para.strip() for para in paragraphs if para.strip() != '']
    return paragraphs

"""
Count occurrences of keywords in each text.
"""
def count_keywords(texts: list, keywords: list) -> list:
    keyword_counts = []
    for text in texts:
        count = sum(text.lower().count(keyword.lower()) for keyword in keywords)
        keyword_counts.append(count)
    return keyword_counts

"""
Identify the sequence of texts that have the maximum count of keywords.
"""
def find_max_keyword_sequence(keyword_counts: list, sequence_length: int = 2):
    max_sum = 0
    start_index = 0
    for i in range(len(keyword_counts) - sequence_length + 1):
        current_sum = sum(keyword_counts[i:i + sequence_length])
        if current_sum > max_sum:
            max_sum = current_sum
            start_index = i
    return start_index

"""
Wrapper for cleaning text
"""
def clean_text(item: str, keywords: list, sequence_length: int = 2):
    text_list = clean_and_split_text(item)
    text_counts = count_keywords(text_list, keywords)
    start_index = find_max_keyword_sequence(text_counts, sequence_length)
    best_item_texts = text_list[start_index:start_index+sequence_length]
    item_cleaned = ". \n ".join(best_item_texts)
    item_cleaned = re.sub(r's \n\n', '', item_cleaned)
    item_cleaned = re.sub(r'\n\nTa', '', item_cleaned)
    return item_cleaned
