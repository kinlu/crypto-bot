import requests
import time


class FinazonProcessor:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"apikey {api_key}"}

    def fetch_time_series(self, dataset, ticker, interval, page_size, request_delay=0):

        querystring = {"dataset": dataset, "ticker": ticker, "interval": interval,
                       "page_size": page_size}
        response = requests.get(f'{self.base_url}/latest/time_series', headers=self.headers, params=querystring)
        time.sleep(request_delay)  # Ensure the time module is imported
        return response.json()
