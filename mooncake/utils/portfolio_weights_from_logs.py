import pandas as pd
from io import StringIO

# Read the entire text file
# Note: Have to go in and delete the '2011-12-30 16:00:00 ' part from the start of the line for it to read correctly
with open('data/output/qc_logs_1.txt', 'r') as file:
    lines = file.readlines()

# Find the line where "Portfolio weights df is:" appears
start_index = next(i for i, line in enumerate(lines) if "Portfolio weights df is:" in line) + 1

# Extract the content from that line onward
data_lines = lines[start_index:]

# Convert the list of lines into a single string and then into a DataFrame
data_str = ''.join(data_lines)

df = pd.read_csv(StringIO(data_str))

# Remove the final row of text
df = df[:-1]

start_date = "2010-01-01"
df = df.query("date >= @start_date")

print(df)
df.to_csv("data/output/portfolio_weights.csv")