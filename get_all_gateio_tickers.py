import requests, json
import os

# Data source API
FINAZON_URL = os.getenv('FINAZON_URL', "https://api.finazon.io/latest/time_series")
FINAZON_API_KEY = os.getenv('FINAZON_API_KEY')


def make_external_request(url, headers, querystring):
    return requests.get(url, headers=headers, params=querystring).json()


def get_tickers_with_publisher_from_api(publisher="gate"):
    page = 0
    all_tickers = []

    while True:
        # Replace this with the actual 'requests.get' call in a live environment.
        response = make_external_request(
            url=FINAZON_URL,
            headers={"Authorization": f"apikey {FINAZON_API_KEY}"},
            querystring={"dataset": publisher, "page": str(page), "page_size": "1000"}
        )
        data = response["data"]
        if not data:  # If data is empty, break the loop.
            break
        # Filter tickers by the specified publisher.
        filtered_tickers = [item["ticker"] for item in data
                            if item["publisher"] == publisher
                            and item["ticker"].endswith('/USDT')
                            and '3L' not in item['ticker']
                            and '3S' not in item['ticker']
                            and '5L' not in item['ticker']
                            and '5S' not in item['ticker']]
        all_tickers.extend(filtered_tickers)
        page += 1  # Prepare for the next page in the next iteration.

    return all_tickers


# Fetch all tickers published by "gate" and save to a JSON file.
usdt_tickers_from_api = get_tickers_with_publisher_from_api("gate")

# Since we're simulating, let's assume usdt_tickers_from_api contains the same data as before
# and proceed to save it to a JSON file.
file_path_from_api = 'resource/tickers_list.json'

with open(file_path_from_api, 'w') as file:
    json.dump(usdt_tickers_from_api, file)
