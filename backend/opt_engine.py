from typing import List, Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd



@dataclass
class Data:
    """Data class to hold historical prices and perform relevant calculations on them"""
    table: pd.DataFrame
    objects: dict = field(default_factory=dict)

    def __post_init__(self):
        self.num_assets: int = len(self.table.columns)

    @property
    def pct_data(self) -> pd.DataFrame:
        """Returns dataframe with daily percentage changes of the prices"""
        if "pct" not in self.objects.keys():
            self.objects["pct"] = self.table.pct_change().apply(lambda x: np.log(1 + x))
        return self.objects["pct"]

    @property
    def cov_matrix(self) -> pd.DataFrame:
        """Returns a covariance matrix of the daily percentage changes of 
        the prices"""
        if "cov" not in self.objects.keys():
            self.objects["cov"] = self.pct_data.cov()
        return self.objects["cov"]


def calculate_volatility(data: Data, weights: List[float]) -> float:
    """Calculates volatility (annual standard deviation of price changes) 
    of a given portfolio"""
    var = data.cov_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()  # Portfolio Variance
    sd = np.sqrt(var)  # Daily standard deviation
    ann_sd = sd * np.sqrt(250)  # Annual standard deviation = volatility
    return ann_sd


def calculate_individual_expected_returns(data: Data) -> np.array:
    """Calculates the individual expected returns vector"""
    return data.table.resample('Y').last().pct_change().mean().to_numpy()


def calculate_expected_returns(ind_er: np.array, weights: List[float]) -> float:
    """Returns the product of expected returns of individual assets
    with the weights of those assets in a given portfolio""" 
    return np.dot(weights, ind_er)  


class TabuSearch:
    """Generic tabu search implementation. Source: https://towardsdatascience.com/optimization-techniques-tabu-search-36f197ef8e25"""
    def __init__(self, init_solution, 
                 func: Callable, neighbor_operator, 
                 aspiration_criteria: Callable, 
                 acceptable_threshold, 
                 tenure: int):
        self.currSolution = init_solution
        self.bestSolution = init_solution
        self.evaluate = func
        self.aspirationCriteria = aspiration_criteria
        self.neighborOperator = neighbor_operator
        self.acceptableScoreThreshold = acceptable_threshold
        self.tabuTenure = tenure
        
    def isTerminationCriteriaMet(self):
        # can add more termination criteria
        return self.evaluate(self.bestSolution) < self.acceptableScoreThreshold \
            or self.neighborOperator(self.currSolution) == 0

    def run(self):
        tabuList = {}
        
        while not self.isTerminationCriteriaMet():
            # get all of the neighbors
            neighbors = self.neighborOperator(self.currSolution)
            # find all tabuSolutions other than those
            # that fit the aspiration criteria
            tabuSolutions = tabuList.keys()
            # find all neighbors that are not part of the Tabu list
            neighbors = filter(lambda n: self.aspirationCriteria(n), neighbors)
            # pick the best neighbor solution
            newSolution = sorted(neighbors, key=lambda n: self.evaluate(n))[0]
            # get the cost between the two solutions
            cost = self.evaluate(self.solution) - self.evaluate(newSolution)
            # if the new solution is better, 
            # update the best solution with the new solution
            if cost >= 0:
                self.bestSolution = newSolution
            # update the current solution with the new solution
            self.currSolution = newSolution
            
            # decrement the Tabu Tenure of all tabu list solutions
            for sol in tabuList:
                tabuList[sol] -= 1
                if tabuList[sol] == 0:
                    del tabuList[sol]
            # add new solution to the Tabu list
            tabuList[newSolution] = self.tabuTenure

        # return best solution found
        return self.bestSolution