import pyreadstat
import pandas as pd

# Define the input .sas7bdat file and output .csv file
input_file = './mooncake/sp500list/sp500cik.sas7bdat'  # Replace with your actual .sas7bdat file
output_file = 'sp500list.csv'  # Replace with your desired CSV filename

# Read the .sas7bdat file into a Pandas DataFrame
df, meta = pyreadstat.read_sas7bdat(input_file)

# Write the DataFrame to a CSV file
df.to_csv(output_file, index=False)

print(f"Data from {input_file} has been successfully written to {output_file}")
