import pandas as pd
import re

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
    
    item_1A = item_search("ITEM 1A RISK FACTORS(.*?)ITEM 1B", content)
    # item_1A
    
    item_1B = item_search("ITEM 1B UNRESOLVED STAFF COMMENTS(.*?)ITEM 2", content)
    # item_1B
    
    item_2 = item_search("ITEM 2 PROPERTIES(.*?)ITEM 3", content)
    # item_2
    
    item_3 = item_search("ITEM 3 LEGAL PROCEEDINGS(.*?)ITEM 4", content)
    
    item_4 = item_search("ITEM 4 MINE SAFETY DISCLOSURES(.*?)ITEM 5", content)
    
    item_5 = item_search("ITEM 5 MARKET FOR REGISTRANT S COMMON EQUITY, RELATED STOCKHOLDER MATTERS AND ISSUER PURCHASES OF EQUITY SECURITIES(.*?)ITEM 6", content)
    
    item_6 = item_search("ITEM 6 SELECTED FINANCIAL DATA(.*?)ITEM 7", content)
    
    item_7 = item_search("ITEM 7 MANAGEMENT S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS(.*?)ITEM 7A", content)
    
    item_7A = item_search("ITEM 7A QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK(.*?)ITEM 8", content)
    
    item_8 = item_search("ITEM 8 FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA(.*?)ITEM 9", content)
    
    item_9 = item_search("ITEM 9 CHANGES IN AND DISAGREEMENTS WITH ACCOUNTANTS ON ACCOUNTING AND FINANCIAL DISCLOSURE(.*?)ITEM 9A", content)
    
    item_9A = item_search("ITEM 9A CONTROLS AND PROCEDURES(.*?)ITEM 9B", content)
    
    item_9B = item_search("ITEM 9B OTHER INFORMATION(.*?)ITEM 10", content)
    
    item_10 = item_search("ITEM 10 DIRECTORS, EXECUTIVE OFFICERS AND CORPORATE GOVERNANCE(.*?)ITEM 11", content)
    
    item_11 = item_search("ITEM 11 EXECUTIVE COMPENSATION(.*?)ITEM 12", content)
    
    item_12 = item_search("ITEM 12 SECURITY OWNERSHIP OF CERTAIN BENEFICIAL OWNERS AND MANAGEMENT AND RELATED STOCKHOLDER MATTERS(.*?)ITEM 13", content)
    
    item_13 = item_search("ITEM 13 CERTAIN RELATIONSHIPS AND RELATED TRANSACTIONS, AND DIRECTOR INDEPENDENCE(.*?)ITEM 14", content)
    
    item_14 = item_search("ITEM 14 PRINCIPAL ACCOUNTING FEES AND SERVICES(.*?)ITEM 15", content)
    
    item_15 = item_search("ITEM 15 EXHIBITS, FINANCIAL STATEMENTS, SCHEDULES FINANCIAL STATEMENTS(.*?)REPORT OF INDEPENDENT REGISTERED PUBLIC ACCOUNTING FIRM", content)
    
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
filename = 'mooncake/10Ks/20230103_10-K_edgar_data_1487931_0001477932-23-000012.txt'
df = extract_text_from_10ks(filename)

df.to_csv("mooncake/10Ks/example_items.csv")