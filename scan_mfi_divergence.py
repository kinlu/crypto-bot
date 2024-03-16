import asyncio
import json
import os

import pandas as pd

from common_function import make_ticker_string
from interface.discord_messager import send_discord_message
from interface.finazon_processor import FinazonProcessor
from quantitative_algo.mfi_calculator import calculate_mfi
from service.charting import detect_bullish_divergence_with_mfi

FINAZON_URL = os.getenv('FINAZON_URL', "https://api.finazon.io")
FINAZON_API_KEY = os.getenv('FINAZON_API_KEY')

# Finazon Request configurations
finazon_processor = FinazonProcessor(FINAZON_URL, FINAZON_API_KEY)
DATA_SET = os.getenv('DATA_SET', 'gate')
TIMESERIES_INTERVAL = os.getenv('TIMESERIES_INTERVAL', '1d')

with open('resource/tickers_list.json', 'r') as file:
    tickers_list = json.load(file)

for ticker in tickers_list:
    print(f'Fetching time series for {ticker}')
    time_series = finazon_processor.fetch_time_series(DATA_SET, ticker, TIMESERIES_INTERVAL, 100, 2)

    if not time_series['data']:
        print(f'No time series available for {ticker}')
        continue

    print('Calculating MFI')
    data = time_series['data']
    # Reverse the data list to order from earliest to latest
    data_reversed = data[::-1]
    # Instantiate the MFI calculator and calculate MFI
    df_mfi = calculate_mfi(data_reversed)
    if df_mfi.empty or len(df_mfi) < 2:
        print(f'No enough MFI data available for {ticker}')
        continue
    # remove last record
    df_mfi = df_mfi[:-1]
    # Convert to dictionary format as specified
    result_dict = {'result': df_mfi.to_dict(orient='records')}

    # Save to JSON file
    print('Saving the MFI results to a JSON file')
    output_file_path = './mfi_result.json'
    with open(output_file_path, 'w') as file:
        json.dump(result_dict, file)

    # Load the MFI results from the JSON file for plotting
    print('Loading the MFI results from the JSON file for plotting')
    with open(output_file_path, 'r') as file:
        mfi_data = json.load(file)
    # Convert the data to a DataFrame
    mfi_df = pd.DataFrame(mfi_data['result'])
    mfi_df['date'] = pd.to_datetime(mfi_df['date'])

    print('Plotting the MFI and Closing Price Over Time')
    is_bullish_divergence_now = detect_bullish_divergence_with_mfi(
        x=mfi_df['date'],
        mfi=mfi_df['mfi'],
        closing_price=mfi_df['Closing Price'],
        title=f'{ticker} Money Flow Index (MFI) and Closing Price Over Time on {TIMESERIES_INTERVAL} Interval',
        xlabel='Date',
        plot_file_path='./mfi_closing_price.png'
    )

    if is_bullish_divergence_now:
        print(f'Bullish divergence is detected for {ticker} and ending the plot to Discord')
        ticker_str = make_ticker_string(ticker)
        asyncio.run(
            send_discord_message(
                token=os.getenv('DISCORD_BOT_TOKEN'),
                channel_id=int(os.getenv('DISCORD_CHANNEL_ID')),
                message=f'Bullish divergence detected for {ticker_str}!',
                image_path='./mfi_closing_price.png'
            )
        )
