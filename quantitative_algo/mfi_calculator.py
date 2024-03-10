import pandas as pd
import numpy as np


def calculate_mfi(data):
    df = pd.DataFrame(data)
    # Calculate the typical price
    df['typical_price'] = (df['h'] + df['l'] + df['c']) / 3

    # Calculate the raw money flow
    df['raw_money_flow'] = df['typical_price'] * df['v']

    # Calculate the money flow ratio using a 14-day period
    df['positive_flow'] = np.where(df['typical_price'] > df['typical_price'].shift(1), df['raw_money_flow'], 0)
    df['negative_flow'] = np.where(df['typical_price'] < df['typical_price'].shift(1), df['raw_money_flow'], 0)

    # Summing over the 14-day period
    df['positive_flow_14'] = df['positive_flow'].rolling(window=14).sum()
    df['negative_flow_14'] = df['negative_flow'].rolling(window=14).sum()

    # Calculate the money flow index (MFI)
    df['money_flow_ratio'] = df['positive_flow_14'] / df['negative_flow_14']
    df['mfi'] = 100 - (100 / (1 + df['money_flow_ratio']))

    # Adjust the timestamp to AEDT (UTC+11)
    df['date_aedt'] = pd.to_datetime(df['t'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Australia/Sydney')

    # Format the date
    df['date_aedt_formatted'] = df['date_aedt'].dt.strftime('%Y-%m-%d-%H-%M-%S')

    # Return the MFI and the formatted date
    return df[['date_aedt_formatted', 'mfi', 'c']].dropna().rename(columns={'date_aedt_formatted': 'date', 'c': 'Closing Price'})
