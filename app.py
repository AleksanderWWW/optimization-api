from flask import Flask, request, jsonify

from backend.scraper import extract_prices
from core import (
    EfficientFrontierSolver,
    SimulatedAnnealingSolver,
    TabuSearchSolver
)

from utils import extract_request_content


app = Flask(__name__)


@app.route('/api/home')
def home():
    ...


@app.route('/api/optimize/effFrontier', methods=['GET', 'POST'])
def optimize_portfolio_ef():
    tickers, years, num_portfolios, rfr = extract_request_content(request)
    df = extract_prices(tickers, years)
    solver = EfficientFrontierSolver(df, num_portfolios, rfr)
    result = solver.optimize()
    return jsonify(result)


@app.route('/api/optimize/simAnnealing', methods=['GET', 'POST'])
def optimize_portfolio_sa():
    tickers, years, rfr = extract_request_content(request, num_portfolios_needed=False)

    df = extract_prices(tickers, years)


@app.route('/api/optimize/taboo', methods=['GET', 'POST'])
def optimize_portfolio_taboo():
    tickers, years, rfr, tenure, max_iter, \
        n_size, no_n  = extract_request_content(request, "taboo")
    df = extract_prices(tickers, years)
    solver = TabuSearchSolver(df, rfr, tenure, max_iter, n_size, no_n)
    result = solver.optimize()
    return jsonify(result)


@app.route('/api/optimize/', methods=['GET', 'POST'])
def optimize_portfolio_all():
    tickers, years, num_portfolios, rfr = extract_request_content(request)
    df = extract_prices(tickers, years)


if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)