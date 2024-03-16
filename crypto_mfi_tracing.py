import asyncio
import json
import os

import pandas as pd

from interface.discord_messager import send_discord_message
from interface.finazon_processor import FinazonProcessor
from quantitative_algo.mfi_calculator import calculate_mfi
from service.charting import plot_mfi_price_for_divergence


FINAZON_URL = os.getenv('FINAZON_URL', "https://api.finazon.io")
FINAZON_API_KEY = os.getenv('FINAZON_API_KEY')

# Finazon Request configurations
finazon_processor = FinazonProcessor(FINAZON_URL, FINAZON_API_KEY)
TIMESERIES_INTERVAL = os.getenv('TIMESERIES_INTERVAL', '1h')
DATA_SET = os.getenv('DATA_SET', 'binance')
SEND_TO_DISCORD = os.getenv('SEND_TO_DISCORD', False)

ticker = os.getenv('TICKER', 'BTC/USDT')

print(f'Fetching time series for {ticker}')
time_series = finazon_processor.fetch_time_series(DATA_SET, ticker, TIMESERIES_INTERVAL, 150, 0)

print('Calculating MFI')
data = time_series['data']
# Reverse the data list to order from earliest to latest
data_reversed = data[::-1]
# Instantiate the MFI calculator and calculate MFI
df_mfi = calculate_mfi(data_reversed)
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
is_divergence_now = plot_mfi_price_for_divergence(
    x=mfi_df['date'],
    mfi=mfi_df['mfi'],
    closing_price=mfi_df['Closing Price'],
    title=f'{ticker} Money Flow Index (MFI) and Closing Price Over Time on {TIMESERIES_INTERVAL} Interval',
    xlabel='Date',
    plot_file_path='./mfi_closing_price.png'
)

if SEND_TO_DISCORD:
    print('Sending the plot to Discord')
    asyncio.run(
        send_discord_message(
            token=os.getenv('DISCORD_BOT_TOKEN'),
            channel_id=int(os.getenv('DISCORD_CHANNEL_ID')),
            message=f'{ticker} MFI and Closing Price Over Time on {TIMESERIES_INTERVAL} Interval',
            image_path='./mfi_closing_price.png'
        )
    )
    if is_divergence_now["buy_signal"]:
        print('Buy/Sell signal: Buy signal detected')
        asyncio.run(
            send_discord_message(
                token=os.getenv('DISCORD_BOT_TOKEN'),
                channel_id=int(os.getenv('DISCORD_CHANNEL_ID')),
                message=f':green_circle: Buy signal detected for {ticker}'
            )
        )
    if is_divergence_now["sell_signal"]:
        print('Buy/Sell signal: Sell signal detected')
        asyncio.run(
            send_discord_message(
                token=os.getenv('DISCORD_BOT_TOKEN'),
                channel_id=int(os.getenv('DISCORD_CHANNEL_ID')),
                message=f':red_circle: Sell signal detected for {ticker}'
            )
        )
    if is_divergence_now["bullish_divergence"]:
        print('There is a bullish divergence between the MFI and the closing price.')
        asyncio.run(
            send_discord_message(
                token=os.getenv('DISCORD_BOT_TOKEN'),
                channel_id=int(os.getenv('DISCORD_CHANNEL_ID')),
                message=f':green_circle: Bullish Divergence detected between MFI and Closing Price for {ticker}'
            )
        )
        if is_divergence_now["sell_signal"]:
            print('Conflicting signal: Sell signal detected during bullish divergence.')
            asyncio.run(
                send_discord_message(
                    token=os.getenv('DISCORD_BOT_TOKEN'),
                    channel_id=int(os.getenv('DISCORD_CHANNEL_ID')),
                    message=f':warning: Conflicting Signal: Sell signal detected during bullish divergence for {ticker}'
                )
            )
    if is_divergence_now["bearish_divergence"]:
        print('There is a bearish divergence between the MFI and the closing price.')
        asyncio.run(
            send_discord_message(
                token=os.getenv('DISCORD_BOT_TOKEN'),
                channel_id=int(os.getenv('DISCORD_CHANNEL_ID')),
                message=f':red_circle: Bearish Divergence detected between MFI and Closing Price for {ticker}'
            )
        )
        if is_divergence_now["buy_signal"]:
            print('Conflicting signal: Buy signal detected during bearish divergence.')
            asyncio.run(
                send_discord_message(
                    token=os.getenv('DISCORD_BOT_TOKEN'),
                    channel_id=int(os.getenv('DISCORD_CHANNEL_ID')),
                    message=f':warning: Conflicting Signal: Buy signal detected during bearish divergence for {ticker}'
                )
            )
