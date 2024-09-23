import re
import pandas as pd
from datetime import datetime, timedelta

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
    paragraphs = text.split("Table of Contents") # sometimes Table is split in to Table or Ta ble
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
    return item_cleaned