from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from backend.opt_engine import (
    Data, 
    calculate_volatility, 
    calculate_individual_expected_returns, 
    calculate_expected_returns
)


def progress_bar(progress: int, total: int) -> None:
    """Simple in-console progress bar - credit: NeuralNine"""
    percent = 100 * (progress / total)

    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f"\r|{bar}| {percent: .2f}%", end='\r')


class Solver(ABC):
    """Abstract solver class for portfolio optimization"""
    def __init__(self, dataframe: pd.DataFrame, rfr: int) -> None:
        self.data = Data(dataframe)
        self.rfr = rfr

        
    @abstractmethod
    def optimize(self, *args, **kwargs):
        ...


class EfficientFrontierSolver(Solver):
    """Solver implementing efficient-frontier-simulation-based optimization
    algorithm"""
    def __init__(self, dataframe: pd.DataFrame, num_portfolios: int, rfr: int) -> None:
        super().__init__(dataframe, rfr)
        self.num_portfolios = num_portfolios

    def generate_portfolios(self) -> pd.DataFrame:

        p_ret = []  # define an empty array for portfolio returns
        p_vol = []  # define an empty array for portfolio volatility
        p_weights = []  # define an empty array for asset weights

        # this needs to be calculated only once
        # and then dot-producted with given 
        # array of weights
        ind_exp_returns = calculate_individual_expected_returns(self.data)

        print("Performing efficient frontier optimization")
        progress_bar(0, self.num_portfolios)

        for i in range(self.num_portfolios):
            weights = np.random.random(self.data.num_assets)
            weights = weights / np.sum(weights)
            p_weights.append(weights)

            returns = calculate_expected_returns(ind_exp_returns, weights)
            p_ret.append(returns)

            vol = calculate_volatility(self.data, weights) # Annual standard deviation = volatility
            p_vol.append(vol)
            progress_bar(i + 1, self.num_portfolios)

        df = pd.DataFrame({'Returns': p_ret, 'Volatility': p_vol})

        for counter, symbol in enumerate(self.data.table.columns.tolist()):
            df[symbol + ' weight'] = [w[counter] for w in p_weights]

        return df

    def optimize(self) -> dict:
        portfolios = self.generate_portfolios()
        portfolios["Sharpe Ratio"] = (portfolios['Returns'] - self.rfr) / portfolios['Volatility']
        optimal_risky_portfolio = portfolios.iloc[portfolios["Sharpe Ratio"].idxmax()]
        return optimal_risky_portfolio.to_dict()


class SimulatedAnnealingSolver(Solver):
    """Solver implementing simulated annealing optimization algorithm"""
    pass


class TabooSearchSolver(Solver):
    """Solver implementing taboo search optimization algorithm"""
    pass