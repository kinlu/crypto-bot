import requests
import time


class FinazonProcessor:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"apikey {api_key}"}

    def fetch_time_series(self, dataset, ticker, interval, back_date, page_size, request_delay = 0):
        from datetime import datetime, timedelta

        epoch_x_days_ago = int((datetime.now() - timedelta(days=back_date)).timestamp())
        querystring = {"dataset": dataset, "ticker": ticker, "interval": interval, "start_at": epoch_x_days_ago,
                       "page_size": page_size}
        response = requests.get(f'{self.base_url}/latest/time_series', headers=self.headers, params=querystring)
        time.sleep(request_delay)  # Ensure the time module is imported
        return response.json()
