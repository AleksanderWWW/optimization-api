from datetime import date

import pandas as pd
import numpy as np

import backend.opt_engine as opt


class TestData:
    df = pd.DataFrame({"A": [.3, .4, .5],
                        "B": [.7, .1, .3]})
    data = opt.Data(df)

    def test_pct_change_in_objects(self):
        self.data.pct_data
        assert "pct" in self.data.objects

    def cov_matrix_in_objects(self):
        self.data.cov_matrix
        assert "cov" in self.data.objects


class TestCalculations:
    df = pd.DataFrame({"A": [.3, .4, .5],
                        "B": [.7, .1, .3]})
    df.set_index(
        pd.to_datetime([
            date(2021, 5, 4),
            date(2021, 11, 4),
            date(2022, 5, 4)
        ]),
        inplace=True
    )
    data = opt.Data(df)
    weights = np.array([.3, .7])

    def test_volatility_calculation(self):
        ann_sd = opt.calculate_volatility(self.data, self.weights)
        assert np.round(ann_sd, 2) == 23.61

    def test_individual_expected_returns_calculation(self):
        ind_exp_rets = opt.calculate_individual_expected_returns(self.data)
        assert (np.round(ind_exp_rets, 4) == np.array([0.25, 2.  ])).all()

    def test_expected_returns_calculation(self):
        ind_exp_rets = opt.calculate_individual_expected_returns(self.data)
        assert np.round(opt.calculate_expected_returns(self.weights, ind_exp_rets), 4) == 1.475