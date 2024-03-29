import asyncio
from datetime import datetime, timedelta
import json
import os

from common_function import make_ticker_string, get_all_tickers
from interface.discord_messager import send_discord_message

from persistence.db_manager import DBManager
from interface.finazon_processor import FinazonProcessor
from quantitative_algo.volume_analyzer import get_significant_volumes

# Data source API
FINAZON_URL = os.getenv('FINAZON_URL', "https://api.finazon.io")
FINAZON_API_KEY = os.getenv('FINAZON_API_KEY')

# Finazon Request configurations
finazon_processor = FinazonProcessor(FINAZON_URL, FINAZON_API_KEY)
finazon_processor.request_delay = int(os.getenv('REQUEST_DELAY', 2))  # default to 2 seconds for each request to finazon

short_vibration_tolerance = float(os.getenv('PRICE_TOLERANCE', 0.1))  # 10% of the opening price at the closing price
vol_multiplier = float(os.getenv('VOL_TOLERANCE', 8))  # 8 times the volume of the next day
back_date = int(os.getenv('BACK_DATE', 5))  # up to 5 days back

# Database configurations
db_manager = DBManager(os.getenv('DB_URL'))

# Discord configurations
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))  # Make sure to convert CHANNEL_ID to an integer


# Function to send message
async def send_message(title, tickers):
    if tickers:
        tickers_str = ', '.join([make_ticker_string(ticker) for ticker in tickers])
        await send_discord_message(TOKEN, CHANNEL_ID, f'{title}:\n{tickers_str}')
    else:
        print(f'No {title.lower()}')


async def main():
    # Load the tickers_list.json file
    with open('resource/tickers_list.json', 'r') as file:
        tickers_list = json.load(file)
    print('Fetching tickers with significant volumes')
    small_vibration_set, large_vibration_set = get_significant_volumes(finazon_processor, tickers_list,
                                                                       short_vibration_tolerance, vol_multiplier,
                                                                       back_date)

    print('Writing result to the database')
    if small_vibration_set['result']:
        db_manager.add_spike_vol_tickers_low_vibration(small_vibration_set)
    if large_vibration_set['result']:
        db_manager.add_spike_vol_tickers_high_vibration(large_vibration_set)

    print('Retrieving today and yesterday records from the database')
    today_record_small_vibration = db_manager.get_spike_vol_tickers_low_vibration((datetime.now()).strftime("%Y-%m-%d"))
    today_record_high_vibration = db_manager.get_spike_vol_tickers_high_vibration((datetime.now()).strftime("%Y-%m-%d"))
    yesterday_record_small_vibration = db_manager.get_spike_vol_tickers_low_vibration((datetime.now() - timedelta(days=1))
                                                                                      .strftime("%Y-%m-%d"))
    yesterday_record_large_vibration = db_manager.get_spike_vol_tickers_high_vibration((datetime.now() - timedelta(days=1))
                                                                                       .strftime("%Y-%m-%d"))
    # get all tickers from the result as a list
    today_tickers_small_vibration = get_all_tickers(today_record_small_vibration)
    today_tickers_large_vibration = get_all_tickers(today_record_high_vibration)
    yesterday_tickers_small_vibration = get_all_tickers(yesterday_record_small_vibration)
    yesterday_tickers_large_vibration = get_all_tickers(yesterday_record_large_vibration)

    print('Sending results to Discord')
    # Compare today's and yesterday's tickers for new and common tickers in both categories
    new_small_vibration_tickers = list(set(today_tickers_small_vibration) - set(yesterday_tickers_small_vibration))
    new_large_vibration_tickers = list(set(today_tickers_large_vibration) - set(yesterday_tickers_large_vibration))

    common_small_vibration_tickers = list(set(today_tickers_small_vibration) & set(yesterday_tickers_small_vibration))
    common_large_vibration_tickers = list(set(today_tickers_large_vibration) & set(yesterday_tickers_large_vibration))

    # Send new and common tickers message
    await send_message('New vol tickers today with small vibration', new_small_vibration_tickers)
    await send_message('New vol tickers today with large vibration', new_large_vibration_tickers)

    await send_message('Common vol tickers in 2 days with small vibration', common_small_vibration_tickers)
    await send_message('Common vol tickers in 2 days with large vibration', common_large_vibration_tickers)

if __name__ == '__main__':
    asyncio.run(main())
