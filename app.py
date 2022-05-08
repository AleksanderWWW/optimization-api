from crypt import methods
from flask import Flask, request, jsonify

from backend.scraper import extract_prices
from core import simulate

app = Flask(__name__)


@app.route('/api/home')
def home():
    ...


@app.route('/api/optimize/effFrontier', methods=['GET', 'POST'])
def optimize_portfolio_ef():
    content = request.json
    tickers = content["tickers"]
    years = content["years"]
    try:
        num_portfolios = content["num"]
    except KeyError:
        num_portfolios = 10_000
    df = extract_prices(tickers, years)
    result = simulate(df, num_portfolios)
    return jsonify(result)


@app.route('/api/optimize/simAnnealing', methods=['GET', 'POST'])
def optimize_portfolio_sa():
    ...


@app.route('/api/optimize/taboo', methods=['GET', 'POST'])
def optimize_portfolio_taboo():
    ...


@app.route('/api/optimize/', methods=['GET', 'POST'])
def optimize_portfolio_all():
    ...


if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)