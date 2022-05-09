from datetime import date

from backend.scraper import Scraper


class TestScraper:

    def test_scraper_initial_details(self):
        sc = Scraper(
            start=date(2020, 5, 4),
            end = date.today()
        )
        assert sc.details == "Scraper(tickers_loaded: 0, data columns loaded: 0)"

    def test_tickers_set_correctly(self):
        tickers_to_set = ["AXP", "AMGN", "GS", "HD", "IBM"]
        sc = Scraper(
            start=date(2020, 5, 4),
            end = date.today()
        )
        sc.set_tickers(tickers_to_set)

        assert sc.tickers == tickers_to_set

    def test_time_series_has_proper_length(self):
        sc = Scraper(
            start=date(2020, 5, 4),
            end = date(2022, 5, 9)
        )
        sc.get_time_series("IBM")
        ts = sc.all_time_series[0]
        
        assert len(ts) == 509

    def test_scrape_data_produces_sorted_data_frame(self):
        tickers_to_set = ["AXP", "AMGN", "GS", "HD", "IBM"]
        sc = Scraper(
            start=date(2020, 5, 4),
            end = date.today()
        )
        sc.set_tickers(tickers_to_set)
        sc.scrape_data()

        assert sc.data.columns.to_list() == sorted(sc.data.columns.to_list())

    def test_merge_data_frames_produces_df_of_correct_shape(self):
        tickers_to_set = ["AXP", "AMGN", "GS", "HD", "IBM"]
        sc = Scraper(
            start=date(2020, 5, 4),
            end = date(2022, 5, 9)
        )
        sc.set_tickers(tickers_to_set)
        sc.scrape_data()

        assert sc.data.shape == (509, 5)