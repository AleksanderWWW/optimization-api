import queue

from typing import List, Callable, Union
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
    """Tabu search algorithm implementation. 
    Based on: https://towardsdatascience.com/
    optimization-techniques-tabu-search-36f197ef8e25"""
    def __init__(self, 
                 init_solution: np.array, 
                 func: Callable[[np.array], Union[int, float]], 
                 tenure: int,
                 max_iter: int,
                 neighbourhood_size: float = 0.1,
                 no_neighbours: int = 10):
                 
        self.current_solution = init_solution
        self.best_solution = init_solution
        self.func = func
        self.tenure = tenure
        self.max_iter = max_iter
        self.n_size = neighbourhood_size
        self.no_neighbours = no_neighbours

        self.tabu_list = queue.deque()  # FIFO queue

    def _get_neighbours(self) -> List[np.array]:
        result = []
        for _ in range(self.no_neighbours):
            candidate = self.current_solution + np.random.uniform(low=-self.n_size, 
                                                    high=self.n_size, 
                                                    size=len(self.current_solution))
            candidate = np.abs(candidate)
            candidate = candidate / candidate.sum()
            result.append(candidate)
        
        return result


    def add_to_tabu_list(self, x: np.array) -> None:
        if len(self.tabu_list) == self.tenure:
            self.tabu_list.pop()
        self.tabu_list.appendleft(hash(tuple(x)))  # ndarray isn't directly hashable           

    def aspiration_criterium(self, x: np.array) -> bool:
        return self.func(x) < self.func(self.best_solution)

    def select_solution(self) -> np.array:
        neighbours = self._get_neighbours()
        to_select = neighbours[0]

        for n in neighbours:
            if self.func(n) < self.func(to_select):
                to_select = n
        
        return to_select
        
    def run(self):
        for i in range(self.max_iter):
            self.add_to_tabu_list(self.current_solution)
            new_point = self.select_solution()

            if self.aspiration_criterium(new_point):
                self.best_solution = new_point
                self.current_solution = new_point
                continue

            if hash(tuple(new_point)) not in self.tabu_list:
                self.current_solution = new_point

        # return best solution found
        return self.best_solution


class SimulatedAnnealing:
    """Abstract implementation of simulated annealing algorithm"""
    def __init__(self, func, start_x, temp_0, d, alpha, max_iter=1000):
        self.func = func
        self.current_x = start_x
        self.temp = temp_0
        self.n = len(start_x)
        self.d = d
        self.alpha = alpha
        self.max_iter = max_iter
        self.k = 0
        
    def draw_candidate(self):
        return self.current_x + np.random.uniform(low=-self.d, high=self.d, size=self.n)
    
    def prob_transition(self, candidate):
        """Probabilistic transition allows the algorithm to escape from local
        minima and explore the design space further"""
        A_k = min(1, np.e**(-1*(self.func(candidate) - self.func(self.current_x)) / self.temp))

        if np.random.uniform(low=0, high=1) < A_k:
                self.current_x = candidate
                
    def activate(self, candidate):
        if self.func(candidate) <= self.func(self.current_x):
            self.current_x = candidate
        else:
            self.prob_transition(candidate)          
                
    def cool_down(self):
        self.temp *= self.alpha
        
    def run(self):
        while self.k < self.max_iter:
            candidate = self.draw_candidate()
            self.activate(candidate)
            self.cool_down()
            self.k += 1
        return self.current_x