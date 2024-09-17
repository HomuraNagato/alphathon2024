import os
import re
import pandas as pd
import pyreadstat

"""
Extracts the items in a 10K text file
"""
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

def item_search(text: str, content: str) -> str:
    item_match = re.search(f"{text}", content, re.DOTALL)
    item = item_match.group(1).strip() if item_match else 'No text available'
    return item

# Define the filename
filename = 'mooncake/10Ks/2023/QTR1/20230103_10-K_edgar_data_1487931_0001477932-23-000012.txt'
df = extract_text_from_10ks(filename)
df.iloc[:,3:5]

df.to_csv("mooncake/10Ks/example_items.csv")

# ------------------------------------------------
# Get all 10K file names
# all_files looks like the following:
# [[file_1, file_2,...], [file_101, file_102,...],...]
# Where they are nested by quarter for naming issues in the next step 
# ------------------------------------------------

quarters = ["QTR1", "QTR2", "QTR3", "QTR4"]
all_files = []
for quarter in quarters:
    quarter_files = os.listdir(f"mooncake/10Ks/2023/{quarter}")
    files_10ks = [file for file in quarter_files if "10-K_edgar" in file]
    all_files.append(files_10ks)

# Filter the files to include only those that contain "10-K_edgar"

files_sub = files[0:6]
# Print the matching files
for file in files_sub:
    print(file)

# ------------------------------------------------
# Extract text for all files
# ------------------------------------------------
df_10ks = pd.DataFrame()
i=0
for files in all_files: # loop through each quarter
    for file in files: # loop through each file in each quarter
        quarter = quarters[i]
        this_file_path = f"mooncake/10Ks/2023/{quarter}/{file}"
        print("filename is: ", this_file_path)
        this_df = extract_text_from_10ks(this_file_path)
        df_10ks = pd.concat([df_10ks, this_df], ignore_index=True)
    i+=1

df_10ks.tail()
df_10ks.to_csv("df_10ks.csv")

# ------------------------------------------------
# Merge in Tickers
# ------------------------------------------------
sp500_file = 'mooncake/sp500/sp500cik.sas7bdat'

# Read the .sas7bdat file into a Pandas DataFrame
sp500, meta = pyreadstat.read_sas7bdat(sp500_file)


df_10ks_sub = df_10ks.head()
# TODO: match on DATE as well
cik_tickers = sp500[['cik', 'TICKER', 'DATE']].drop_duplicates(ignore_index=True)
# len(cik_tickers)
# cik_tickers

df_10ks2 = df_10ks.merge(cik_tickers, how="left", on="cik")

# merge has lots of missing NAs
df_10ks2.head()["cik"]
sum(df_10ks2["TICKER"].notna())
sp500.query("cik == '0001798272'")
sp500.query("cik == '0001282637'")
sp500.query("cik == '0000089140'")
sp500.query("cik == '0001771225'")
sp500.query("cik == '0001789029'")



df_10ks3 = df_10ks2[df_10ks2["TICKER"].notna()]

df_10ks3.to_csv("df_10ks.csv")