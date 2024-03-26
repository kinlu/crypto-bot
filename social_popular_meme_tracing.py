import asyncio
import os
from interface.discord_messager import send_discord_message
from interface.lunarcrush_processor import LunarCrushProcessor

lunarcrush_api_key = os.getenv('LUNARCRUSH_API_KEY')
discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')
discord_channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))


def create_message_list(coins):
    messages = []

    for coin in coins:
        name = coin['name'][:20] + (coin['name'][20:] and '..')
        symbol = coin['symbol']
        url_name = coin['name'].replace(' ', '-')
        url = f"https://lunarcrush.com/discover/{symbol.lower()}-{url_name.lower()}?metric=close%2Calt\\_rank"

        alt_rank = coin.get('alt_rank', 'N/A')
        alt_rank_previous = coin.get('alt_rank_previous', alt_rank)
        alt_rank_change = alt_rank_previous - alt_rank if alt_rank != 'N/A' and alt_rank_previous != 'N/A' else 0
        alt_rank_arrow = '↑' if alt_rank_change > 0 else '↓' if alt_rank_change < 0 else '→'
        alt_rank_str = f"{'__' if alt_rank_change > 0 else ''}{alt_rank}{'__' if alt_rank_change > 0 else ''} {alt_rank_arrow} {abs(alt_rank_change) if alt_rank_change != 0 else ''}"

        galaxy_score = coin.get('galaxy_score', 'N/A')
        galaxy_score_previous = coin.get('galaxy_score_previous', galaxy_score)
        galaxy_score_change = galaxy_score_previous - galaxy_score if galaxy_score != 'N/A' and galaxy_score_previous != 'N/A' else 0
        galaxy_score_arrow = '↑' if galaxy_score_change > 0 else '↓' if galaxy_score_change < 0 else '→'
        galaxy_score_str = f"{'__' if galaxy_score_change > 0 else ''}{galaxy_score}{'__' if galaxy_score_change > 0 else ''} {galaxy_score_arrow} {abs(galaxy_score_change) if galaxy_score_change != 0 else ''}"

        percent_change_1h = coin.get('percent_change_1h', 'N/A')
        percent_change_1h_str = f"{'__' if percent_change_1h > 0 else ''}{percent_change_1h:.2f}%{'__' if percent_change_1h > 0 else ''}"

        percent_change_24h = coin.get('percent_change_24h', 'N/A')
        percent_change_24h_str = f"{'__' if percent_change_24h > 0 else ''}{percent_change_24h:.2f}%{'__' if percent_change_24h > 0 else ''}"

        percent_change_7d = coin.get('percent_change_7d', 'N/A')
        percent_change_7d_str = f"{'__' if percent_change_7d > 0 else ''}{percent_change_7d:.2f}%{'__' if percent_change_7d > 0 else ''}"

        message = (
            f"**Token Name:** {name}, "
            f"**Symbol:** [{symbol}]({url}), "
            f"**Market Cap Rank:** {coin['market_cap_rank']}, "
            f"**AltRank:** {alt_rank_str}, "
            f"**Galaxy Score:** {galaxy_score_str}, "
            f"**1h Change:** {percent_change_1h_str}, "
            f"**24h Change:** {percent_change_24h_str}, "
            f"**7d Change:** {percent_change_7d_str}"
        )
        messages.append(message)

    return messages


print("Fetching meme coins...")
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
print("Sorting meme coins...")
meme_coins = sorted(meme_coins, key=lambda coin: coin.get('alt_rank', float('inf')))
new_meme_coins = sorted(new_meme_coins, key=lambda coin: coin.get('alt_rank', float('inf')))

print("Creating message lists...")
messages_meme_coins = create_message_list(meme_coins)
messages_new_meme_coins = create_message_list(new_meme_coins)

print("Sending messages to Discord...")
message1 = f"```diff\n+ Found {len(meme_coins)} tokens related to 'meme' with current AltRank in top 100 (sorted by AltRank ascending):\n```"
message2 = messages_meme_coins
message3 = f"```diff\n+ Among them, {len(new_meme_coins)} tokens are new to the top 100 (sorted by AltRank ascending):\n```"
message4 = messages_new_meme_coins

print("Message 1")
asyncio.run(send_discord_message(discord_bot_token, discord_channel_id, message1))

print("Message 2")
asyncio.run(send_discord_message(discord_bot_token, discord_channel_id, message2))

print("Message 3")
asyncio.run(send_discord_message(discord_bot_token, discord_channel_id, message3))

print("Message 4")
asyncio.run(send_discord_message(discord_bot_token, discord_channel_id, message4))
