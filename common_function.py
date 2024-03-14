def get_all_tickers(record):
    tickers = []
    if not record:
        return tickers
    for item in record['spike_vol_tickers']['result']:
        tickers.append(item['ticker'])
    return tickers


def make_ticker_string(ticker_name):
    ticker_name = ticker_name.replace('/', '_')
    ticker_link = f'https://www.gate.io/zh/trade/{ticker_name}'
    ticker_string = f'[{ticker_name}]({ticker_link})'
    return ticker_string
