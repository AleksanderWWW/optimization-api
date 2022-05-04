import datetime as dt

from typing import List, Union

from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor as Executor

import pandas as pd

import pandas_datareader as pdr



@dataclass
class Scraper:
    """Object providing attributes and methods used to extract historical 
    prices of a given set of assets, for a given period of time.
    
    Constructor accepts start and end dates of format datetime.date.
    Upon instantiation, the object has an empty list of tickers.
    Those are set using the set_tickers method of the object."""
    start: dt.date
    end: dt.date
    all_time_series: List[pd.Series] = field(default_factory=list)
    data = pd.DataFrame()
    tickers: List[str] = field(default_factory=list)

    @property
    def details(self) -> str:
        return f"Scraper(tickers_loaded: {len(self.tickers)}, data columns loaded: {len(self.all_time_series)})"

    def set_tickers(self, tickers: List[str]) -> None:
        """Set the tickers to obtain the data for."""
        self.tickers = tickers

    def get_time_series(self, ticker: str, provider: str ="yahoo") -> None:
        """For a given ticker, the method extracts the historical prices for 
        the date range given in the object's constructor.
        The data is in the form of a pandas.DataFrame object.
        It is not returned, but appended to the the all_dfs
        object's attribute of type list."""
        ts = pdr.DataReader(ticker, provider, self.start, self.end)[
            "Adj Close"]  # Only take the Adjusted Close data
        ts = ts.rename(ticker)
        self.all_time_series.append(ts)  # collect the data to a list later used to create the final data set

    def scrape_data(self) -> None:
        
        with Executor(max_workers=30) as executor:
            executor.map(self.get_time_series, self.tickers)
        self.data = self.merge_data_frames()
        self.data = self.data.sort_index(axis=1)  # sort the column names alphabetically (they come in random order)

    def merge_data_frames(self) -> pd.DataFrame:
        df = pd.concat(self.all_time_series,
                       axis=1)  # pandas.concat takes a list of dataframes and creates one big frame
        return df


def extract_prices(tickers: List[str], years: Union[int, float]) -> pd.DataFrame:
    end = dt.date.today()
    start = end - dt.timedelta(days=365 * years)

    sc = Scraper(start=start, end=end)
    sc.set_tickers(tickers)

    sc.scrape_data()

    return sc.data
