import pandas as pd
import numpy as np
from scipy.optimize import minimize

# Sample data
data = {
    "ticker": ["AAPL", "NVDA", "BLK", "AAPL", "NVDA", "BLK", "AAPL", "NVDA", "BLK", "AAPL", "NVDA", "BLK"],
    "date": ["2021-01-01", "2021-01-01", "2021-01-01", "2021-01-02", "2021-01-02", "2021-01-02", "2021-01-03", "2021-01-03", "2021-01-03", "2021-01-04", "2021-01-04", "2021-01-04"],
    "position": ["Buy", "Buy", "Buy", "Buy", "Buy", "Buy", "Buy", "Buy", "Buy", "Buy", "Buy", "Sell"],
    "price": [132, 540, 700, 134, 550, 695, 130, 555, 652, 133, 557, 670]  # Sample prices
}
df = pd.DataFrame(data)

# Filter to only buy positions
buy_df = df.query("position == 'Buy'")
current_month = df['date'].max()
buy_stocks = set(df.query("position == 'Buy'").query("date == @current_month")['ticker'])
sell_stocks = set(df.query("position == 'Sell'").query("date == @current_month")['ticker'])

df_hist = df.query("ticker in @buy_stocks").query("date < @current_month")

# Pivot table to reshape data for returns calculation
price_table = df_hist.pivot_table(values='price', index='date', columns='ticker')

# Calculate daily returns
returns = price_table.pct_change().dropna()

# Annualize the daily returns
annual_returns = returns.mean() * 252
annual_covariance = returns.cov() * 252

# Number of assets
num_assets = len(annual_returns)

# Function to calculate portfolio returns and volatility
def portfolio_performance(weights, mean_returns, cov_matrix):
    returns = np.dot(weights, mean_returns)
    std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return std_dev, returns

# Objective function to minimize (Here we focus on minimizing variance)
def minimize_variance(weights, mean_returns, cov_matrix):
    return portfolio_performance(weights, mean_returns, cov_matrix)[0]

# Constraints (the sum of weights is 1)
constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

# Boundaries for weights
bounds = tuple((0, 1) for asset in range(num_assets))

# Initial guess (equal distribution)
init_guess = num_assets * [1. / num_assets,]

# Minimize variance
optimal_var = minimize(minimize_variance, init_guess, args=(annual_returns, annual_covariance), method='SLSQP', bounds=bounds, constraints=constraints)

# Get the optimal weights
optimal_weights = optimal_var.x

# Calculate expected return and risk of the optimal portfolio
portfolio_std_dev, portfolio_return = portfolio_performance(optimal_weights, annual_returns, annual_covariance)

print("Optimal Weights:", optimal_weights)
print("Expected Annual Return:", portfolio_return)
print("Annual Volatility/Risk:", portfolio_std_dev)

weights = [float(weight) for weight in optimal_weights]
type(weights[1])
list(optimal_weights)
new_portfolio_weights = pd.DataFrame({"ticker": annual_returns.reset_index()["ticker"],
                                      "weights": weights})

sp500_tickers = ["AAPL", "NVDA", "BLK"]

sp500_df = pd.DataFrame({"ticker": sp500_tickers})

sp500_df = sp500_df.merge(new_portfolio_weights, how="left", on="ticker")
sp500_df = sp500_df.fillna(0)
sp500_df


# some stuff to get rebalancing working in QuantConnect
df_rebalance = df.copy()
df_rebalance.sort_values(["ticker", "date"]).groupby("ticker").tail(1)

my_set = set()
my_set.add("a")
my_set.add("b")
my_set.add("c")
my_set.remove(str("c"))
my_set