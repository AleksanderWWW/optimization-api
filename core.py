import numpy as np
import pandas as pd

from backend.opt_engine import Data, calculate_volatility, calculate_individual_expected_returns, calculate_expected_returns


def generate_portfolios(data: Data, num_portfolios: int, num_assets: int) -> pd.DataFrame:

    p_ret = []  # define an empty array for portfolio returns
    p_vol = []  # define an empty array for portfolio volatility
    p_weights = []  # define an empty array for asset weights

    # this needs to be calculated only once
    # and then dot-producted with given 
    # array of weights
    ind_exp_returns = calculate_individual_expected_returns(data)

    for _ in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights = weights / np.sum(weights)
        p_weights.append(weights)

        returns = calculate_expected_returns(ind_exp_returns, weights)
        p_ret.append(returns)

        vol = calculate_volatility(data, weights) # Annual standard deviation = volatility
        p_vol.append(vol)

    df = pd.DataFrame({'Returns': p_ret, 'Volatility': p_vol})

    for counter, symbol in enumerate(data.table.columns.tolist()):
        df[symbol + ' weight'] = [w[counter] for w in p_weights]

    return df


def simulate(table: pd.DataFrame, num_portfolios: int, rf: int) -> dict:
    num_assets = len(table.columns)
    portfolios = generate_portfolios(table, num_portfolios, num_assets)
    portfolios["Sharpe Ratio"] = (portfolios['Returns'] - rf) / portfolios['Volatility']
    optimal_risky_portfolio = portfolios.iloc[portfolios["Sharpe Ratio"].idxmax()]
    return optimal_risky_portfolio.to_dict()