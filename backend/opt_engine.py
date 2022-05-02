from dataclasses import dataclass, field
from abc import ABC, abstractmethod

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


class Calculator(ABC):

    @abstractmethod
    def calculate(self, *args, **kwargs):
        ...


@dataclass
class VolatilityCalculator(Calculator):
    data: Data
    weights: list = field(default_factory=list)

    def calculate(self) -> float:
        var = self.data.cov_matrix.mul(self.weights, axis=0).mul(self.weights, axis=1).sum().sum()  # Portfolio Variance
        sd = np.sqrt(var)  # Daily standard deviation
        ann_sd = sd * np.sqrt(250)  # Annual standard deviation = volatility
        return ann_sd


@dataclass
class ExpectedReturnsCalculator(Calculator):
    data: Data
    weights: list = field(default_factory=list)

    def calculate(self) -> float:
        ind_er = self.data.table.resample('Y').last().pct_change().mean()
        return np.dot(self.weights, ind_er)  # Returns are the product of individual expected returns of asset and its
        # weights


@dataclass
class SharpeRatioCalculator(Calculator):
    risk_free_rate: float
    data: Data
    weights: list = field(default_factory=list)

    def calculate(self):
        vol = VolatilityCalculator(self.data, self.weights).calculate()
        er = ExpectedReturnsCalculator(self.data, self.weights).calculate()

        return (er - self.risk_free_rate) / vol
