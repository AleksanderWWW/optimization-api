def progress_bar(progress: int, total: int) -> None:
    """Simple in-console progress bar - credit: NeuralNine"""
    percent = 100 * (progress / total)

    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f"\r|{bar}| {percent: .2f}%", end='\r')