from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from backend.opt_engine import (
    Data, 
    calculate_volatility, 
    calculate_individual_expected_returns, 
    calculate_expected_returns,
    TabuSearch
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
        self.ind_exp_returns = calculate_individual_expected_returns(self.data)

        
    @abstractmethod
    def optimize(self, *args, **kwargs) -> dict:
        ...


class Metaheuristic(Solver):
    def __init__(self, dataframe: pd.DataFrame, rfr: int) -> None:
        super().__init__(dataframe, rfr)

    def objective_function(self, x: np.array) -> float:
        """Function that will be optimised by the implemented metaheuristic"""

        returns = calculate_expected_returns(self.ind_exp_returns, x)
        vol = calculate_volatility(self.data, x) # Annual standard deviation = volatility
        return (returns - self.rfr) / vol

    def optimize(self, *args, **kwargs):
        return super().optimize(*args, **kwargs)


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

        print("Performing efficient frontier optimization")
        progress_bar(0, self.num_portfolios)

        for i in range(self.num_portfolios):
            weights = np.random.random(self.data.num_assets)
            weights = weights / np.sum(weights)
            p_weights.append(weights)

            returns = calculate_expected_returns(self.ind_exp_returns, weights)
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


class SimulatedAnnealingSolver(Metaheuristic):
    """Solver implementing simulated annealing optimization algorithm"""
    pass


class TabuSearchSolver(Metaheuristic):
    """Solver implementing taboo search optimization algorithm"""
    def __init__(self, dataframe: pd.DataFrame, rfr: int, threshold: int) -> None:
        super().__init__(dataframe, rfr)     
        self.threshold = threshold   

    def _neighbourhood_op(self):
        ...

    def _aspiration_crit(self):
        ...

    def optimize(self) -> dict:
        """Initialize starting point and run the tabu search procedure"""
        

        x0 = np.random.random(self.data.num_assets)

        tabu_search = TabuSearch(
            init_solution=x0,
            neighbor_operator=self._neighbourhood_op,
            aspiration_criteria=self._aspiration_crit,
            acceptable_threshold=self.threshold
        )

        chosen_weights = tabu_search.run()
        
        result = {symbol + " weight": w for symbol, w in zip(
            self.data.table.columns, 
            chosen_weights)}

        result["Sharpe ratio"] = self.objective_function(chosen_weights)
        result["Volatility"] = calculate_volatility(self.data, chosen_weights)
        result["Returns"] = calculate_expected_returns(self.ind_exp_returns, chosen_weights)

        return result