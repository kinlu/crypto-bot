import requests
from datetime import datetime, timedelta
import time


def is_within_short_vibration_tolerance(closing, opening, tolerance):
    gap_low = opening
    gap_high = opening * (1 + tolerance)
    return gap_low <= closing <= gap_high


def is_within_large_vibration_tolerance(closing, opening, tolerance):
    gap_low = opening * (1 + tolerance)
    return gap_low <= closing


class FinazonProcessor:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"apikey {api_key}"}
        self.short_vibration_tolerance = 0
        self.vol_multiplier = 0
        self.back_date = 0
        self.request_delay = 0

    small_vibration_set = {"result": []}
    large_vibration_set = {"result": []}

    def fetch_time_series(self, dataset, ticker, interval, back_date, page_size, request_delay):
        epoch_x_days_ago = int((datetime.now() - timedelta(days=back_date)).timestamp())
        querystring = {"dataset": dataset, "ticker": ticker, "interval": interval, "start_at": epoch_x_days_ago,
                       "page_size": page_size}
        response = requests.get(f'{self.base_url}/latest/time_series', headers=self.headers, params=querystring)
        time.sleep(request_delay)  # Ensure the time module is imported
        return response.json()

    def get_significant_volumes(self, tickers_list):
        for ticker in tickers_list:
            print(f'Fetching volume data for {ticker}')
            volume_data = self.fetch_time_series("gate", ticker, "1d", self.back_date, 15, self.request_delay)
            spike_volumes_with_small_vibration = []
            spike_volumes_with_large_vibration = []

            for i in range(len(volume_data["data"]) - 1):
                current_item = volume_data["data"][i]
                next_item = volume_data["data"][i + 1]
                current_item["t"] = datetime.utcfromtimestamp(current_item["t"]).strftime('%Y-%m-%d')
                if current_item["v"] >= next_item["v"] * self.vol_multiplier:
                    if is_within_short_vibration_tolerance(current_item["c"], current_item["o"],
                                                           self.short_vibration_tolerance):
                        spike_volumes_with_small_vibration.append(current_item)
                    elif is_within_large_vibration_tolerance(current_item["c"], current_item["o"],
                                                             self.short_vibration_tolerance):
                        spike_volumes_with_large_vibration.append(current_item)

            if spike_volumes_with_small_vibration:
                self.small_vibration_set["result"].append({"ticker": ticker,
                                                           "significant_volumes": spike_volumes_with_small_vibration})

            if spike_volumes_with_large_vibration:
                self.large_vibration_set["result"].append({"ticker": ticker,
                                                           "significant_volumes": spike_volumes_with_large_vibration})
