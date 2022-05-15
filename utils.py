def progress_bar(progress: int, total: int) -> None:
    """Simple in-console progress bar - credit: NeuralNine"""
    percent = 100 * (progress / total)

    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f"\r|{bar}| {percent: .2f}%", end='\r')


def extract_request_content(request, num_portfolios_needed=True):
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

    if num_portfolios_needed:
        try:
            num_portfolios = content["num"]
        except KeyError:
            num_portfolios = 10_000
        return tickers, years, num_portfolios, rfr
    else:
        return tickers, years, rfr
    