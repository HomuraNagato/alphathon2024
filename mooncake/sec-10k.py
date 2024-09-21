import os
import re
import pandas as pd
import pyreadstat
from datetime import datetime, timedelta

# ------------------------------------------------
# Read in S&P500 data
# ------------------------------------------------
sp500_file = 'mooncake/sp500/sp500cik.sas7bdat'
# Read the .sas7bdat file into a Pandas DataFrame
sp500, meta = pyreadstat.read_sas7bdat(sp500_file)

# ------------------------------------------------
# Function to extract the items text in 10K files
# ------------------------------------------------
def extract_text_from_10ks(filename: str) -> pd.DataFrame:
    with open(filename, 'r') as file:
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
    item_1A = item_search("ITEM 1A(.*?)ITEM 1B", content)
    # item_1A
    item_1B = item_search("ITEM 1B(.*?)ITEM 2", content)
    # item_1B
    item_2 = item_search("ITEM 2(.*?)ITEM 3", content)
    # item_2
    item_3 = item_search("ITEM 3(.*?)ITEM 4", content)
    item_4 = item_search("ITEM 4(.*?)ITEM 5", content)
    item_5 = item_search("ITEM 5(.*?)ITEM 6", content)
    item_6 = item_search("ITEM 6(.*?)ITEM 7", content)
    item_7 = item_search("ITEM 7(.*?)ITEM 7A", content)
    item_7A = item_search("ITEM 7A(.*?)ITEM 8", content)
    item_8 = item_search("ITEM 8(.*?)ITEM 9", content)
    item_9 = item_search("ITEM 9(.*?)ITEM 9A", content)
    item_9A = item_search("ITEM 9A(.*?)ITEM 9B", content)
    item_9B = item_search("ITEM 9B(.*?)ITEM 10", content)
    item_10 = item_search("ITEM 10(.*?)ITEM 11", content)
    item_11 = item_search("ITEM 11(.*?)ITEM 12", content)
    item_12 = item_search("ITEM 12(.*?)ITEM 13", content)
    item_13 = item_search("ITEM 13(.*?)ITEM 14", content)
    item_14 = item_search("ITEM 14(.*?)ITEM 15", content)
    item_15 = item_search("ITEM 15(.*?)REPORT OF INDEPENDENT REGISTERED PUBLIC ACCOUNTING FIRM", content)
    item_16 = item_search("REPORT OF INDEPENDENT REGISTERED PUBLIC ACCOUNTING FIRM(.*?)LIABILITIES AND STOCKHOLDERS' DEFICIT", content)
    item_17 = item_search("LIABILITIES AND STOCKHOLDERS' DEFICIT(.*?)CONSOLIDATED STATEMENTS", content)
    data = {
        'cik': [cik],
        'company_name': [company_name],
        'date': [date],
        'item_1A': [item_1A],
        'item_1B': [item_1B],
        'item_2': [item_2],
        'item_3': [item_3],
        'item_4': [item_4],
        'item_5': [item_5],
        'item_6': [item_6],
        'item_7': [item_7],
        'item_7A': [item_7A],
        'item_8': [item_8],
        'item_9': [item_9],
        'item_9A': [item_9A],
        'item_9B': [item_9B],
        'item_10': [item_10],
        'item_11': [item_11],
        'item_12': [item_12],
        'item_13': [item_13],
        'item_14': [item_14],
        'item_15': [item_15],
        'item_16': [item_16],
        'item_17': [item_17],
    }
    return pd.DataFrame(data)

"""
Helper function to search for and extract text using regular expressions
"""
def item_search(text: str, content: str) -> str:
    item_match = re.search(f"{text}", content, flags=re.DOTALL)
    item = item_match.group(1).strip() if item_match else 'No text available'
    return item

# Define the filename
# filename = 'mooncake/10Ks/2023/QTR1/20230103_10-K_edgar_data_1487931_0001477932-23-000012.txt'
# df = extract_text_from_10ks(filename)
# df.iloc[:,3:5]

# df.to_csv("mooncake/10Ks/example_items.csv")

# ------------------------------------------------
# Get all 10K file names
# all_files will look like the following:
#   [[file_1, file_2,...], [file_101, file_102,...],...]
# Where they are nested by quarter for naming issues in the next step 
# ------------------------------------------------

quarters = ["QTR1", "QTR2", "QTR3", "QTR4"]
all_files = []
for quarter in quarters:
    quarter_files = os.listdir(f"mooncake/10Ks/2023/{quarter}")
    # Filter the files to include only those that contain "10-K_edgar"
    files_10ks = [file for file in quarter_files if "10-K_edgar" in file]
    all_files.append(files_10ks)

files_count = sum([len(files) for files in all_files])

# ------------------------------------------------
# Extract text for all files
# ------------------------------------------------
df_10ks = pd.DataFrame()
i=0; j = 0
for files in all_files: # loop through each quarter
    for file in files: # loop through each file in each quarter
        if j % int(files_count/10) == 0:
            print(f"We are {j // int(files_count/10)}0% through")
        quarter = quarters[i]
        this_file_path = f"mooncake/10Ks/2023/{quarter}/{file}"
        # print("filename is: ", this_file_path)
        this_df = extract_text_from_10ks(this_file_path)
        df_10ks = pd.concat([df_10ks, this_df], ignore_index=True)
        j+=1
    i+=1

df_10ks.tail()
# df_10ks.to_csv("df_10ks.csv")
# type(df_10ks['cik'][0])

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

sp500["date"] = sp500['DATE'].apply(lambda x: convert_sas_date(x, '%Y-%m-%d'))
sp500["ym"] = sp500['DATE'].apply(lambda x: convert_sas_date(x, '%Y-%m'))

df_10ks['DATE'] = df_10ks['date'].copy()
df_10ks['date'] = df_10ks['DATE'].apply(lambda x: convert_10ks_date(x, '%Y-%m-%d'))
df_10ks['ym'] = df_10ks['DATE'].apply(lambda x: convert_10ks_date(x, '%Y-%m'))

# ------------------------------------------------
# Merge 10k dataframe with tickers in S&P500
# ------------------------------------------------
sp500.rename(columns={"TICKER": "ticker"}, inplace=True)
sp500[['cik', 'ticker', 'date', 'ym']].head()
df_10ks[['cik', 'date', 'ym']].head()

cik_tickers_map = sp500[['cik', 'ym', 'ticker']].drop_duplicates(ignore_index=True)
len(cik_tickers_map)
cik_tickers_map.head()

# df_10ks['cik'] = df_10ks['cik'].astype(str)
df_10ks2 = df_10ks.merge(cik_tickers_map, how="left", on=["cik", "ym"])
df_10ks2[['cik', 'date', 'ym', 'ticker']]

# df_10ks.query("cik == '0001282637'")
# cik_tickers_date.query("cik == '0001282637'")

df_10ks3 = df_10ks2[df_10ks2['ticker'].notna()]

# merge has lots of missing NAs
# df_10ks2.head()["cik"]
# sum(df_10ks2["TICKER"].notna())
# sp500.query("cik == '0001798272'")
# sp500.query("cik == '0001282637'")
# sp500.query("cik == '0000089140'")
# sp500.query("cik == '0001771225'")
# sp500.query("cik == '0001789029'")

df_10ks3.to_csv("mooncake/10Ks/df_10ks.csv")

df_10ks3 = pd.read_csv("mooncake/10Ks/df_10ks.csv", dtype={"cik": str})
df_10ks3.head()

# ------------------------------------------------
# Further clean data
# Some texts are up to 30 paragraphs long, this is too large to pass in to an LLM
# So let's split the text into paragraph chunks, count the number of keywords in each,
# and then take the 5 sequential texts that have the largest count (the most relevant section)
# ------------------------------------------------
df_10ks3[['item_1A']].iloc[3,:][0][17:120]
keywords = ["risk", "financial", "performance", "dividend", "buyback", "operations", "market", "legal", "increase", "decrease"]
sequence_length = 5
item_cols = [col for col in df_10ks3.columns if "item" in col]

"""
Split the text into an array
"""
def clean_and_split_text(text: str):
    # Remove 'Table of Contents' and any preceding numbers
    cleaned_text = re.sub(r"\d+\s*\nTable of Contents\s*\n", "", text)
    # Remove company name in capital letters (assumed to be a line of uppercase words)
    cleaned_text = re.sub(r"^[A-Z\s]+\n", "\n", cleaned_text, flags=re.MULTILINE)
    # Split text into paragraphs
    paragraphs = cleaned_text.split('\n\n')
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

# test it out
text_list = clean_and_split_text(df_10ks3[['item_1A']].iloc[3,:][0])
text_list_test = ["there is one risk facter here", "there are two important risk factors here", "and two important risk factors here", "nothing here"]
text_counts = count_keywords(text_list_test, keywords)
text_counts

start_index = find_max_keyword_sequence(text_counts, sequence_length = 2)
text_list_test[start_index:start_index+2]

# and apply to all columns
# for items columns
df_10ks3_clone = df_10ks3.copy()
df_10ks3 = df_10ks3_clone.copy()
df_10ks3.reset_index(inplace=True)
n = len(df_10ks3)
for item in item_cols:
    print("item is", item)
    for i in range(10):
        this_item_text = df_10ks3.at[i, item]
        if len(this_item_text[0:50]) >= 50:
            print(f"row {i} will be processed")
            text_list = clean_and_split_text(this_item_text)
            text_counts = count_keywords(text_list, keywords)
            start_index = find_max_keyword_sequence(text_counts, sequence_length)
            best_item_texts = text_list[start_index:start_index+sequence_length]
        else:
            best_item_text = ""
        df_10ks3.at[i, item] = ". \n ".join(best_item_texts)
    
len(df_10ks3['item_1A'][44])
# reduced df_10ks3_clone['item_1A'][44] from 133546 to 15789 characters
# can also include a value of the decrease in file size in terms of megabytes

df_10ks4 = df_10ks3.copy()
df_10ks4.to_csv("mooncake/10Ks/df_10ks_l5_cleaned.csv")