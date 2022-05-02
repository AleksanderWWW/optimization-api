from typing import List
from dataclasses import dataclass, field

import numpy as np
import pandas as pd



@dataclass
class Data:
    table: pd.DataFrame
    objects: dict = field(default_factory=dict)

    @property
    def pct_data(self):
        if "pct" not in self.objects.keys():
            self.objects["pct"] = self.table.pct_change().apply(lambda x: np.log(1 + x))
        return self.objects["pct"]

    @property
    def cov_matrix(self):
        if "cov" not in self.objects.keys():
            self.objects["cov"] = self.pct_data.cov()
        return self.objects["cov"]



def calculate_volatility(data: Data, weights: List[float]) -> float:
    var = data.cov_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()  # Portfolio Variance
    sd = np.sqrt(var)  # Daily standard deviation
    ann_sd = sd * np.sqrt(250)  # Annual standard deviation = volatility
    return ann_sd


def calculate_expected_returns(data: Data, weights: List[float]) -> float:
    ind_er = data.table.resample('Y').last().pct_change().mean()
    # Returns are the product of individual expected returns of asset and its weights
    return np.dot(weights, ind_er)  
