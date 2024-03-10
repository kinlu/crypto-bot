from _datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi


def get_spike_vol_tickers(date, collection):
    try:
        return collection.find_one({"date": date})
    except Exception as e:
        print(e)


def add_spike_vol_tickers(volume, collection):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        data = {"date": current_date, "spike_vol_tickers": volume}
        # check if the record for the current date already exists
        if collection.find_one({"date": current_date}):
            # if it exists, update the record
            collection.update_one({"date": current_date}, {"$set": {"spike_vol_tickers": volume}})
        else:
            collection.insert_one(data)
    except Exception as e:
        print(e)


class DBManager:
    def __init__(self, uri):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client['gateio']
        self.low_vibration_collection_name = 'spike_vol_ticker_records_low_vibration'
        self.high_vibration_collection_name = 'spike_vol_ticker_records_high_vibration'

    def add_spike_vol_tickers_low_vibration(self, volume):
        add_spike_vol_tickers(volume, self.db[self.low_vibration_collection_name])

    def add_spike_vol_tickers_high_vibration(self, volume):
        add_spike_vol_tickers(volume, self.db[self.high_vibration_collection_name])

    def get_spike_vol_tickers_low_vibration(self, date):
        return get_spike_vol_tickers(date,
                                     self.db[self.low_vibration_collection_name])

    def get_spike_vol_tickers_high_vibration(self, date):
        return get_spike_vol_tickers(date,
                                     self.db[self.high_vibration_collection_name])
