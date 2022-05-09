from flask import Flask, request, jsonify

from backend.scraper import extract_prices
from core import (
    EfficientFrontierSolver,
    SimulatedAnnealingSolver,
    TabooSearchSolver
)


app = Flask(__name__)


@app.route('/api/home')
def home():
    ...


@app.route('/api/optimize/effFrontier', methods=['GET', 'POST'])
def optimize_portfolio_ef():
    content = request.json
    tickers = content["tickers"]

    try:
        years = content["years"]
    except KeyError:
        years = 1

    try:
        num_portfolios = content["num"]
    except KeyError:
        num_portfolios = 10_000

    try:
        rfr = content["rfr"]
    except KeyError:
        rfr = 0.01
    df = extract_prices(tickers, years)
    solver = EfficientFrontierSolver(df, num_portfolios, rfr)
    result = solver.optimize()
    return jsonify(result)


@app.route('/api/optimize/simAnnealing', methods=['GET', 'POST'])
def optimize_portfolio_sa():
    content = request.json
    tickers = content["tickers"]

    try:
        years = content["years"]
    except KeyError:
        years = 1
    
    try:
        rfr = content["rfr"]
    except KeyError:
        rfr = 0.01

    df = extract_prices(tickers, years)


@app.route('/api/optimize/taboo', methods=['GET', 'POST'])
def optimize_portfolio_taboo():
    ...


@app.route('/api/optimize/', methods=['GET', 'POST'])
def optimize_portfolio_all():
    ...


if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)