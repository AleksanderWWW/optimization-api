algos = ["frontier", "taboo", "annealing"]


def progress_bar(progress: int, total: int) -> None:
    """Simple in-console progress bar - credit: NeuralNine"""
    percent = 100 * (progress / total)

    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f"\r|{bar}| {percent: .2f}%", end='\r')


def extract_request_content(request, algorithm: str):
       
    content = request.json
    tickers = content["tickers"]

    years = content["years"]

    rfr = content["rfr"]

    if algorithm == "frontier":
        try:
            num_portfolios = content["num"]
        except KeyError:
            num_portfolios = 10_000
        return tickers, years, num_portfolios, rfr

    elif algorithm == "taboo":
        tenure = content["tenure"]
        max_iter = content["max_iter"]
        neighbourhood_size = content["neighbourhood_size"]
        no_neighbours = content["no_neighbours"]

        return tickers, years, tenure, max_iter, neighbourhood_size, no_neighbours
    
    elif algorithm == "annealing":
        temp_0 = content["temp_0"]
        neighbourhood_size = content["neighbourhood_size"]
        alpha = content["alpha"]
        max_iter = content["max_iter"]

        return tickers, years, temp_0, neighbourhood_size, alpha, max_iter

    else:
        raise Exception(f"Algoritm {algorithm} not recognized. Viable options are: {algos}")
    