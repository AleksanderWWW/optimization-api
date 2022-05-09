from typing import List
from dataclasses import dataclass, field

import numpy as np
import pandas as pd



@dataclass
class Data:
    """Data class to hold historical prices and perform relevant calculations on them"""
    table: pd.DataFrame
    num_assets: int = len(table)
    objects: dict = field(default_factory=dict)

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
