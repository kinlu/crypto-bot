import asyncio
import os
from prettytable import PrettyTable
from interface.discord_messager import send_discord_message
from interface.lunarcrush_processor import LunarCrushProcessor

lunarcrush_api_key = os.getenv('LUNARCRUSH_API_KEY')
discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')
discord_channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))


def create_table(coins):
    table = PrettyTable()
    table.field_names = ["Token Name", "Symbol", "Market Cap Rank", "AltRank", "Galaxy Score", "1h Change", "24h Change", "7d Change"]
    table.align["Token Name"] = "l"
    table.align["Symbol"] = "c"

    for coin in coins:
        name = coin['name'][:20] + (coin['name'][20:] and '..')
        symbol = coin['symbol']

        alt_rank_str = get_rank_str(coin, 'alt_rank')
        galaxy_score_str = get_rank_str(coin, 'galaxy_score')

        percent_change_1h = f"{coin.get('percent_change_1h', 'N/A'):.2f}%"
        percent_change_24h = f"{coin.get('percent_change_24h', 'N/A'):.2f}%"
        percent_change_7d = f"{coin.get('percent_change_7d', 'N/A'):.2f}%"

        table.add_row([name, symbol, coin['market_cap_rank'], alt_rank_str, galaxy_score_str, percent_change_1h, percent_change_24h, percent_change_7d])

    return table


def get_rank_str(coin, rank_key):
    rank = coin.get(rank_key, 'N/A')
    previous_rank = coin.get(f'{rank_key}_previous', rank)
    rank_change = previous_rank - rank if rank != 'N/A' and previous_rank != 'N/A' else 'N/A'
    rank_arrow = '↑' if rank_change > 0 else '↓' if rank_change < 0 else '→'
    return f"{rank} {rank_arrow} {abs(rank_change) if rank_change != 'N/A' else ''}"


processor = LunarCrushProcessor(lunarcrush_api_key)
data = processor.get_top_coins(sort="alt_rank")

meme_coins = [
    coin for coin in data['data']
    if 'meme' in coin.get('categories', []) and coin.get('alt_rank', float('inf')) <= 100
]

new_meme_coins = [
    coin for coin in meme_coins
    if coin.get('alt_rank_previous', float('inf')) > 100
]

# 按照AltRank从小到大排序
meme_coins = sorted(meme_coins, key=lambda coin: coin.get('alt_rank', float('inf')))
new_meme_coins = sorted(new_meme_coins, key=lambda coin: coin.get('alt_rank', float('inf')))

table1 = create_table(meme_coins)
table2 = create_table(new_meme_coins)

message1 = (f"Found {len(meme_coins)} tokens related to 'meme' with current AltRank in top 100 (sorted by AltRank "
            f"ascending):\n```\n{table1}\n```\n")
message2 = f"Among them, {len(new_meme_coins)} tokens are new to the top 100 (sorted by AltRank ascending):\n```\n{table2}\n```"

asyncio.run(send_discord_message(discord_bot_token, discord_channel_id, message=message1))
asyncio.run(send_discord_message(discord_bot_token, discord_channel_id, message=message2))
