import os
import re
import pandas as pd
import pyreadstat
from datetime import datetime, timedelta
from utils.utilities import extract_text_from_10x, convert_sas_date, convert_10ks_date, clean_and_split_text, count_keywords, find_max_keyword_sequence

keywords = ["risk", "financial", "performance", "dividend", "buyback", "operations", "market", "legal", "increase", "decrease"]
sequence_length = 2

"""
form_style should be: '10-K' or '10-Q'
"""
def process_forms(form_style: str, year: str):
    print(f"Starting processing for Form-{form_style}-{year}")
    # ------------------------------------------------
    # Read in S&P500 data
    # ------------------------------------------------
    sp500_file = 'sp500list/sp500cik.sas7bdat'
    # Read the .sas7bdat file into a Pandas DataFrame
    sp500, meta = pyreadstat.read_sas7bdat(sp500_file)
    sp500.rename(columns={"TICKER": "ticker"}, inplace=True)
    # sp500.head()
    sp500_ciks = sp500[['cik']].drop_duplicates(ignore_index=True)
    # Define the filename
    # file_name = '10Ks/2023/QTR1/20230103_10-K_edgar_data_1487931_0001477932-23-000012.txt'
    file_name = '10Ks/2023/QTR1/20230130_10-K_edgar_data_1035443_0001035443-23-000099.txt'
    # df = extract_text_from_10ks(filename)
    # df.iloc[:,3:5]
    # df.to_csv("mooncake/10Ks/example_items.csv")
    # ------------------------------------------------
    # Get all 10K file names
    # all_files will look like the following:
    #   [[file_1, file_2,...], [file_101, file_102,...],...]
    # Where they are nested by quarter for naming issues in the next step 
    # ------------------------------------------------
    print("Collecting files")
    quarters = ["QTR1", "QTR2", "QTR3", "QTR4"]
    all_files = []
    for quarter in quarters:
        quarter_files = os.listdir(f"10Ks/{year}/{quarter}")
        # Filter the files to include only those that contain "10-K_edgar"
        files = [file for file in quarter_files if f"{form_style}_edgar" in file]
        all_files.append(files)
    #
    files_count = sum([len(files) for files in all_files])
    # len(all_files[0])
    # ------------------------------------------------
    # Extract text for all files
    # ------------------------------------------------
    df_10x1 = pd.DataFrame()
    i=0; j = 0
    for files in all_files: # loop through each quarter
        for file in files: # loop through each file in each quarter
            if j % int(files_count/10) == 0:
                print(f"We are {j // int(files_count/10)}0% through text extraction")
            # if j >= 100:
            #     continue
            quarter = quarters[i]
            this_file_path = f"10Ks/{year}/{quarter}/{file}"
            # print("filename is: ", this_file_path)
            this_df = extract_text_from_10x(this_file_path, form_style, keywords, sp500_ciks, sequence_length)
            df_10x1 = pd.concat([df_10x1, this_df], ignore_index=True)
            j+=1
        i+=1
    # df_10x1.tail()
    # df_10x1["item_1A"][34]
    # df_10ks.to_csv("df_10ks.csv")
    # type(df_10ks['cik'][0])
    # ------------------------------------------------
    # Align dates
    # ------------------------------------------------
    sp500["date"] = sp500['DATE'].apply(lambda x: convert_sas_date(x, '%Y-%m-%d'))
    sp500["ym"] = sp500['DATE'].apply(lambda x: convert_sas_date(x, '%Y-%m'))
    # sp500[['cik', 'ticker', 'date', 'ym']].head()
    # df_10x1[['cik', 'date', 'ym']].head()
    df_10x1['DATE'] = df_10x1['date'].copy()
    df_10x1['date'] = df_10x1['DATE'].apply(lambda x: convert_10ks_date(x, '%Y-%m-%d'))
    df_10x1['ym'] = df_10x1['DATE'].apply(lambda x: convert_10ks_date(x, '%Y-%m'))
    # ------------------------------------------------
    # Merge 10k dataframe with tickers in S&P500
    # ------------------------------------------------
    cik_tickers_map = sp500[['cik', 'ym', 'ticker']].drop_duplicates(ignore_index=True)
    # len(cik_tickers_map)
    # cik_tickers_map.head()
    # df_10ks['cik'] = df_10ks['cik'].astype(str)
    df_10x2 = df_10x1.merge(cik_tickers_map, how="left", on=["cik", "ym"])
    # df_10x2[['cik', 'date', 'ym', 'ticker']]
    # df_10x1.query("cik == '0001282637'")
    # cik_tickers_date.query("cik == '0001282637'")
    df_10x3 = df_10x2[df_10x2['ticker'].notna()]
    # merge has lots of missing NAs
    # df_10x2.head()["cik"]
    # sum(df_10x2["TICKER"].notna())
    # sp500.query("cik == '0001798272'")
    # sp500.query("cik == '0001282637'")
    # sp500.query("cik == '0000089140'")
    # sp500.query("cik == '0001771225'")
    # sp500.query("cik == '0001789029'")
    # df_10x3.to_csv("10Ks/df_10ks.csv")
    # df_10x3 = pd.read_csv(f"10Ks/df_10_{form_style}_{year}.csv", dtype={"cik": str})
    # df_10x3.head()
    # ------------------------------------------------
    # Further clean data
    # Some texts are up to 30 paragraphs long, this is too large to pass in to an LLM
    # So let's split the text into paragraph chunks, count the number of keywords in each,
    # and then take the 5 sequential texts that have the largest count (the most relevant section)
    # ------------------------------------------------
    # print("Cleaning text")
    # df_10ks3[['item_1A']].iloc[3,:][0][17:120]
    # item_cols = [col for col in df_10x3.columns if "item" in col]
    # test it out
    # text_list = clean_and_split_text(df_10x3[['item_1A']].iloc[3,:][0])
    # text_list_test = ["there is one risk facter here", "there are two financial risk factors here", "and two legal risk factors here", "three increase decrease dividends"]
    # text_counts = count_keywords(text_list_test, keywords)
    # text_counts
    # start_index = find_max_keyword_sequence(text_counts, sequence_length)
    # text_list_test[start_index:start_index+2]
    # and apply to all columns
    # for items columns
    # df_10x3_clone = df_10x3.copy()
    # df_10ks3 = df_10ks3_clone.copy()
    # df_10x3.reset_index(inplace=True)
    # n = len(df_10x3)
    # for item in item_cols:
    #     # print("item is", item)
    #     for i in range(n):
    #         this_item_text = df_10x3.at[i, item]
    #         if len(this_item_text[0:50]) >= 50:
    #             # print(f"row {i} will be processed")
    #             text_list = clean_and_split_text(this_item_text)
    #             text_counts = count_keywords(text_list, keywords)
    #             start_index = find_max_keyword_sequence(text_counts, sequence_length)
    #             best_item_texts = text_list[start_index:start_index+sequence_length]
    #         else:
    #             best_item_texts = ""
    #         df_10x3.at[i, item] = ". \n ".join(best_item_texts)
    # len(df_10ks3_clone['item_1A'][44])
    # len(df_10ks3['item_1A'][3])
    # reduced df_10ks3_clone['item_1A'][44] from 133555 to 10805 characters (l2) 20733 characters (l5)
    # can also include a value of the decrease in file size in terms of megabytes
    # df_10x4 = df_10x3.copy()
    df_10x3.to_csv(f"10Ks/form-{form_style}-{year}.csv")
    print(f"Form-{form_style}-{year} finished processing")
    return 0

years = [str(year) for year in range(2001, 2023)]
# for year in years:
year = "2001"
process_forms(form_style = "10-K", year = year)