import json
import pandas as pd
import pyreadstat
from utils.utilities import convert_sas_date
import plotly.express as px

# ------------------------------------------------
# Extract the portfolio returns from QuantConnect output
# ------------------------------------------------

# Parse the JSON data
with open('data/output/qc_output_1.json', 'r') as file:
    data = json.load(file)

# Extract the values from the nested dictionary
values = data['charts']['Strategy Equity']['series']['Equity']['values']
portfolio_value = [value[1] for value in values]
portfolio_value = portfolio_value[::2] # it looks like it is repeating the values twice

# Convert it into a DataFrame
df = pd.DataFrame({"price": portfolio_value})

print(df)
df['price']
df['portfolio_return'] = df['price'].pct_change()
df.at[0, "portfolio_return"] = 0
df['portfolio_return'].cumsum()

start_date = "2010-01-01"
n = df.shape[0]

# ------------------------------------------------
# Get the sp500 returns
# ------------------------------------------------
sp500, meta = pyreadstat.read_sas7bdat('data/sp500s/sp500.sas7bdat')
sp500["date"] = sp500['datadate'].apply(lambda x: convert_sas_date(x, '%Y-%m-%d'))
sp500_2 = sp500.query("date >= @start_date").head(n).reset_index()
sp500_2.at[0, "logsp500ret"] = 0
sp500_2 = sp500_2[["date", "logsp500ret"]]
sp500_2.rename(columns={"logsp500ret": "sp500_return"}, inplace=True)

# ------------------------------------------------
# Merge them together
# ------------------------------------------------
df['date'] = sp500_2['date']
df_2 = df.merge(sp500_2, how = 'left', on = 'date')
df_2 = df_2[["date", "sp500_return", "portfolio_return"]]

# ------------------------------------------------
# Plot
# ------------------------------------------------

# Convert the 'date' column to datetime
df_2['date_2'] = pd.to_datetime(df['date'])

# Create a Plotly figure
fig = px.line(df_2, x='date_2', y=['portfolio_return', 'sp500_return'],
              labels={'value': 'Returns', 'date_2': 'Date'},
              title='Return vs S&P 500 Return',
              template="plotly")

# Customize layout
fig.update_layout(
    legend_title_text='Series',
    yaxis_title='Return',
    xaxis_title='Date'
)

# Show the plot
fig.show()
