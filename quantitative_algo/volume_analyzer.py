from datetime import datetime
from finazon_processor import FinazonProcessor


def is_within_short_vibration_tolerance(closing, opening, tolerance):
    gap_low = opening
    gap_high = opening * (1 + tolerance)
    return gap_low <= closing <= gap_high


def is_within_large_vibration_tolerance(closing, opening, tolerance):
    gap_low = opening * (1 + tolerance)
    return gap_low <= closing


def get_significant_volumes(processor: FinazonProcessor, tickers_list, short_vibration_tolerance, vol_multiplier, back_date):
    small_vibration_set = {"result": []}
    large_vibration_set = {"result": []}

    for ticker in tickers_list:
        print(f'Fetching volume data for {ticker}')
        volume_data = processor.fetch_time_series("gate", ticker, "1d", back_date, 15, 2)
        spike_volumes_with_small_vibration = []
        spike_volumes_with_large_vibration = []

        for i in range(len(volume_data["data"]) - 1):
            current_item = volume_data["data"][i]
            next_item = volume_data["data"][i + 1]
            current_item["t"] = datetime.utcfromtimestamp(current_item["t"]).strftime('%Y-%m-%d')
            if current_item["v"] >= next_item["v"] * vol_multiplier:
                if is_within_short_vibration_tolerance(current_item["c"], current_item["o"],
                                                       short_vibration_tolerance):
                    spike_volumes_with_small_vibration.append(current_item)
                elif is_within_large_vibration_tolerance(current_item["c"], current_item["o"],
                                                         short_vibration_tolerance):
                    spike_volumes_with_large_vibration.append(current_item)

        if spike_volumes_with_small_vibration:
            small_vibration_set["result"].append({"ticker": ticker,
                                                  "significant_volumes": spike_volumes_with_small_vibration})

        if spike_volumes_with_large_vibration:
            large_vibration_set["result"].append({"ticker": ticker,
                                                  "significant_volumes": spike_volumes_with_large_vibration})

    return small_vibration_set, large_vibration_set
