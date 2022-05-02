import numpy as np
import pandas as pd

from opt_engine import VolatilityCalculator, ExpectedReturnsCalculator, Data


def generate_portfolios(table: pd.DataFrame, num_portfolios: int) -> pd.DataFrame:
    data = Data(table)
    num_assets = len(table.columns)
    p_ret = []  # Define an empty array for portfolio returns
    p_vol = []  # Define an empty array for portfolio volatility
    p_weights = []  # Define an empty array for asset weights

    for _ in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights = weights / np.sum(weights)
        p_weights.append(weights)

        returns = ExpectedReturnsCalculator(data, weights).calculate()
        p_ret.append(returns)

        vol = VolatilityCalculator(data, weights).calculate()  # Annual standard deviation = volatility
        p_vol.append(vol)

    df = pd.DataFrame({'Returns': p_ret, 'Volatility': p_vol})

    for counter, symbol in enumerate(data.table.columns.tolist()):
        df[symbol + ' weight'] = [w[counter] for w in p_weights]

    return df


def simulate(table, num_portfolios=10_000, rf=0.01) -> dict:
    portfolios = generate_portfolios(table, num_portfolios)
    portfolios["Sharpe Ratio"] = (portfolios['Returns'] - rf) / portfolios['Volatility']
    optimal_risky_port = portfolios.iloc[portfolios["Sharpe Ratio"].idxmax()]
    return optimal_risky_port.to_dict()