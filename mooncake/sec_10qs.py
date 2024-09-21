# ------------------------------------------------
# Do the same for Quarterly reports
# ------------------------------------------------
import os
import re
import pandas as pd
import pyreadstat

from utils.utilities import item_search, convert_sas_date, convert_10ks_date, clean_and_split_text, count_keywords, find_max_keyword_sequence

# ------------------------------------------------
# Read in S&P500 data
# ------------------------------------------------
sp500_file = 'sp500/sp500cik.sas7bdat'
# Read the .sas7bdat file into a Pandas DataFrame
sp500, meta = pyreadstat.read_sas7bdat(sp500_file)

# ------------------------------------------------
# Function to extract the items text in 10K files
# ------------------------------------------------
def extract_text_from_10qs(filename: str) -> pd.DataFrame:
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
    item_1A = item_search("(ITEM 1A|Item 1A|ITEM 1|Item 1\.)(.*?)(ITEM 1B|2 Unregistered|2. Unregistered)", content)
    # item_1A
    item_2 = item_search("(ITEM 1B|2 Unregistered|2. Unregistered)(.*?)(ITEM 3|3 Defaults|3. Defaults)", content)
    # item_2
    item_3 = item_search("(ITEM 3|3 Defaults|3. Defaults)(.*?)(ITEM 4|4 Mine|4. Mine)", content)
    # item_3
    item_4 = item_search("(ITEM 4|4 Mine|4. Mine)(.*?)(ITEM 5|5 Other|5. Other)", content)
    # item_4
    item_5 = item_search("(ITEM 5|5 Other|5. Other)(.*?)(ITEM 6|6 Exhibits|6. Exhibits)", content)
    # item_5
    data = {
        'cik': [cik],
        'company_name': [company_name],
        'date': [date],
        'item_1A': [item_1A],
        'item_2': [item_2],
        'item_3': [item_3],
        'item_4': [item_4],
        'item_5': [item_5]
    }
    return pd.DataFrame(data)

quarters = ["QTR1", "QTR2", "QTR3", "QTR4"]
all_quarterly_files = []
for quarter in quarters:
    quarter_files = os.listdir(f"10Ks/2023/{quarter}")
    # Filter the files to include only those that contain "10-K_edgar"
    files_10qs = [file for file in quarter_files if "10-Q_edgar" in file]
    all_quarterly_files.append(files_10qs)

quarterly_files_count = sum([len(files) for files in all_quarterly_files])

df_10qs = pd.DataFrame()
i=0; j = 0
for files in all_quarterly_files: # loop through each quarter
    for file in files: # loop through each file in each quarter
        if j % int(quarterly_files_count/10) == 0:
            print(f"We are {j // int(quarterly_files_count/10)}0% through")
        # file = all_quarterly_files[0][0]
        quarter = quarters[i]
        this_file_path = f"10Ks/2023/{quarter}/{file}"
        # print("filename is: ", this_file_path)
        this_df = extract_text_from_10qs(this_file_path)
        df_10qs = pd.concat([df_10qs, this_df], ignore_index=True)
        j+=1
    i+=1
  
# ------------------------------------------------
# Align dates
# ------------------------------------------------

sp500["date"] = sp500['DATE'].apply(lambda x: convert_sas_date(x, '%Y-%m-%d'))
sp500["ym"] = sp500['DATE'].apply(lambda x: convert_sas_date(x, '%Y-%m'))

df_10qs['DATE'] = df_10qs['date'].copy()
df_10qs['date'] = df_10qs['DATE'].apply(lambda x: convert_10ks_date(x, '%Y-%m-%d'))
df_10qs['ym'] = df_10qs['DATE'].apply(lambda x: convert_10ks_date(x, '%Y-%m'))

# ------------------------------------------------
# Merge 10k dataframe with tickers in S&P500
# ------------------------------------------------
sp500.rename(columns={"TICKER": "ticker"}, inplace=True)
sp500[['cik', 'ticker', 'date', 'ym']].head()
df_10qs[['cik', 'date', 'ym']].head()

cik_tickers_map = sp500[['cik', 'ym', 'ticker']].drop_duplicates(ignore_index=True)
len(cik_tickers_map)
cik_tickers_map.head()

# df_10ks['cik'] = df_10ks['cik'].astype(str)
df_10qs2 = df_10qs.merge(cik_tickers_map, how="left", on=["cik", "ym"])
df_10qs2[['cik', 'date', 'ym', 'ticker']]

# df_10ks.query("cik == '0001282637'")
# cik_tickers_date.query("cik == '0001282637'")

df_10qs3 = df_10qs2[df_10qs2['ticker'].notna()]

# merge has lots of missing NAs
# df_10ks2.head()["cik"]
# sum(df_10ks2["TICKER"].notna())
# sp500.query("cik == '0001798272'")
# sp500.query("cik == '0001282637'")
# sp500.query("cik == '0000089140'")
# sp500.query("cik == '0001771225'")
# sp500.query("cik == '0001789029'")

df_10qs3.to_csv("10Ks/df_10qs.csv")

# df_10ks3 = pd.read_csv("10Ks/df_10ks.csv", dtype={"cik": str})
# df_10ks3.head()

# ------------------------------------------------
# Further clean data
# Some texts are up to 30 paragraphs long, this is too large to pass in to an LLM
# So let's split the text into paragraph chunks, count the number of keywords in each,
# and then take the 5 sequential texts that have the largest count (the most relevant section)
# ------------------------------------------------
df_10qs3[['item_1A']].iloc[3,:][0][17:120]
keywords = ["risk", "financial", "performance", "dividend", "buyback", "operations", "market", "legal", "increase", "decrease"]
sequence_length = 5
item_cols = [col for col in df_10qs3.columns if "item" in col]

# test it out
text_list = clean_and_split_text(df_10qs3[['item_1A']].iloc[3,:][0])
text_list_test = ["there is one risk facter here", "there are two important risk factors here", "and two important risk factors here", "nothing here"]
text_counts = count_keywords(text_list_test, keywords)
text_counts

start_index = find_max_keyword_sequence(text_counts, sequence_length = 2)
text_list_test[start_index:start_index+2]

# and apply to all columns
# for items columns
df_10qs3_clone = df_10qs3.copy()
# df_10qs3 = df_10qs3_clone.copy()
df_10qs3.reset_index(inplace=True)
n = len(df_10qs3)
for item in item_cols:
    print("item is", item)
    for i in range(n):
        this_item_text = df_10qs3.at[i, item]
        if len(this_item_text[0:50]) >= 50:
            print(f"row {i} will be processed")
            text_list = clean_and_split_text(this_item_text)
            text_counts = count_keywords(text_list, keywords)
            start_index = find_max_keyword_sequence(text_counts, sequence_length)
            best_item_texts = text_list[start_index:start_index+sequence_length]
        else:
            best_item_texts = ""
        df_10qs3.at[i, item] = ". \n ".join(best_item_texts)
    
len(df_10qs3_clone['item_1A'][24])
len(df_10qs3['item_1A'][2])
# reduced df_10qs3_clone['item_1A'][24] from 147306 to 18398 characters
# can also include a value of the decrease in file size in terms of megabytes

df_10qs4 = df_10qs3.copy()
df_10qs4.to_csv("10Ks/df_10qs_l5_cleaned.csv")