from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from backend.opt_engine import (
    Data, 
    calculate_volatility, 
    calculate_individual_expected_returns, 
    calculate_expected_returns,
    SimulatedAnnealing,
    TabuSearch
)

from utils import progress_bar


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
        return -1 * (returns - self.rfr) / vol  # -1 because we want to minimize the objective function

    def generate_start_point(self):
        x0 = np.random.random(self.data.num_assets)
        x0 = np.abs(x0)
        x0 = x0 / x0.sum()
        return x0

    def generate_result(self, chosen_weights: list) -> dict:
        result = {symbol + " weight": w for symbol, w in zip(
            self.data.table.columns, 
            chosen_weights)}

        result["Sharpe ratio"] = -1 * self.objective_function(chosen_weights)
        result["Volatility"] = calculate_volatility(self.data, chosen_weights)
        result["Returns"] = calculate_expected_returns(self.ind_exp_returns, chosen_weights)

        return result

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
    def __init__(self, dataframe: pd.DataFrame, 
                 rfr: int,
                 temp_0: float,
                 neighbourhood_size: float,
                 alpha: float,
                 max_iter: int) -> None:
        super().__init__(dataframe, rfr)
        self.temp_0 = temp_0
        self.neighbourhood_size = neighbourhood_size
        self.alpha = alpha
        self.max_iter = max_iter

    def optimize(self) -> dict:
        x0 = self.generate_start_point()
        annealing_engine = SimulatedAnnealing(
            func=self.objective_function,
            start_x=x0,
            temp_0=self.temp_0,
            d=self.neighbourhood_size,
            alpha=self.alpha,
            max_iter=self.max_iter
        )

        chosen_weights = annealing_engine.run()

        return self.generate_result(chosen_weights)



class TabuSearchSolver(Metaheuristic):
    """Solver implementing taboo search optimization algorithm"""
    def __init__(self, dataframe: pd.DataFrame, rfr: int, 
                 tenure: int,
                 max_iter: int, 
                 neighbour_size: float = 0.1,
                 no_neighbours: int = 10) -> None:
        super().__init__(dataframe, rfr)       
        self.tenure = tenure
        self.max_iter = max_iter
        self.neighbour_size = neighbour_size
        self.no_neighbours = no_neighbours

    def optimize(self) -> dict:
        """Initialize starting point and run the tabu search procedure"""
        x0 = self.generate_start_point()

        tabu_search = TabuSearch(
            func=self.objective_function,
            init_solution=x0,
            tenure=self.tenure,
            max_iter=self.max_iter,
            neighbourhood_size=self.neighbourhood_size,
            no_neighbours=self.no_neighbours
        )

        chosen_weights = tabu_search.run()
        
        return self.generate_result(chosen_weights)
        