import pandas as pd
from interface.lunarcrush_processor import LunarCrushProcessor
from rich.console import Console
from rich.table import Table


def create_rich_table(df, title):
    table = Table(title=title)
    table.add_column("Index", justify="center", style="cyan")
    table.add_column("Token Name", justify="left", style="cyan")
    table.add_column("Symbol", justify="center", style="magenta")
    table.add_column("Market Cap Rank", justify="center", style="green")
    table.add_column("AltRank", justify="center")
    table.add_column("Galaxy Score", justify="center")
    table.add_column("1h Change", justify="center")
    table.add_column("24h Change", justify="center")
    table.add_column("7d Change", justify="center")
    table.add_column("Blockchains", justify="left", style="blue")

    for index, row in df.iterrows():
        name = row['name'][:20] + (row['name'][20:] and '..')
        symbol = row['symbol']
        url_name = row['name'].replace(' ', '-')
        url = f"https://lunarcrush.com/discover/{symbol.lower()}-{url_name.lower()}?metric=close%2Calt_rank"

        alt_rank = row.get('alt_rank', 'N/A')
        alt_rank_previous = row.get('alt_rank_previous', alt_rank)
        alt_rank_change = alt_rank_previous - alt_rank if alt_rank != 'N/A' and alt_rank_previous != 'N/A' else 0
        alt_rank_arrow = '↑' if alt_rank_change > 0 else '↓' if alt_rank_change < 0 else '→'
        alt_rank_color = "green" if alt_rank_change > 0 else "red" if alt_rank_change < 0 else "white"
        alt_rank_str = f"[{alt_rank_color}]{alt_rank} {alt_rank_arrow} {abs(alt_rank_change) if alt_rank_change != 0 else ''}[/{alt_rank_color}]"

        galaxy_score = row.get('galaxy_score', 'N/A')
        galaxy_score_previous = row.get('galaxy_score_previous', galaxy_score)
        galaxy_score_change = galaxy_score_previous - galaxy_score if galaxy_score != 'N/A' and galaxy_score_previous != 'N/A' else 0
        galaxy_score_arrow = '↑' if galaxy_score_change > 0 else '↓' if galaxy_score_change < 0 else '→'
        galaxy_score_color = "green" if galaxy_score_change > 0 else "red" if galaxy_score_change < 0 else "white"
        galaxy_score_str = f"[{galaxy_score_color}]{galaxy_score} {galaxy_score_arrow} {abs(galaxy_score_change) if galaxy_score_change != 0 else ''}[/{galaxy_score_color}]"

        percent_change_1h = row.get('percent_change_1h', 'N/A')
        percent_change_1h_color = "green" if percent_change_1h > 0 else "red" if percent_change_1h < 0 else "white"
        percent_change_1h_str = f"[{percent_change_1h_color}]{percent_change_1h:.2f}%[/{percent_change_1h_color}]"

        percent_change_24h = row.get('percent_change_24h', 'N/A')
        percent_change_24h_color = "green" if percent_change_24h > 0 else "red" if percent_change_24h < 0 else "white"
        percent_change_24h_str = f"[{percent_change_24h_color}]{percent_change_24h:.2f}%[/{percent_change_24h_color}]"

        percent_change_7d = row.get('percent_change_7d', 'N/A')
        percent_change_7d_color = "green" if percent_change_7d > 0 else "red" if percent_change_7d < 0 else "white"
        percent_change_7d_str = f"[{percent_change_7d_color}]{percent_change_7d:.2f}%[/{percent_change_7d_color}]"

        blockchains = row.get('blockchains', [])
        if isinstance(blockchains, list):
            blockchains_str = "\n".join([f"{bc['network']} - {bc['address']}" for bc in blockchains])
        else:
            blockchains_str = "N/A"

        table.add_row(
            str(index + 1),
            name,
            f"[link={url}]{symbol}[/link]",
            str(row['market_cap_rank']),
            alt_rank_str,
            galaxy_score_str,
            percent_change_1h_str,
            percent_change_24h_str,
            percent_change_7d_str,
            blockchains_str
        )

    return table


def report_coins(lunarcrush_api_key):
    print("Fetching meme coins...")
    processor = LunarCrushProcessor(lunarcrush_api_key)
    data = processor.get_top_coins(sort="alt_rank")

    df = pd.DataFrame(data['data'])

    meme_coins_df = df[df['categories'].astype(str).str.contains('meme') & (df['alt_rank'] <= 100)]
    new_meme_coins_df = meme_coins_df[meme_coins_df['alt_rank_previous'] > 100]

    print("Sorting meme coins...")
    meme_coins_df = meme_coins_df.sort_values('alt_rank')
    new_meme_coins_df = new_meme_coins_df.sort_values('alt_rank')

    console = Console(record=True, width=200)

    # Create the HTML file for meme_coins_df
    print("Creating HTML files...")
    table_meme_coins = create_rich_table(meme_coins_df, "Meme Coins")
    console.print(table_meme_coins)
    html_meme_coins = console.export_html(inline_styles=True)
    with open("meme_coins.html", "w") as f:
        f.write(html_meme_coins)

    # Create the HTML file for new_meme_coins_df
    table_new_meme_coins = create_rich_table(new_meme_coins_df, "New Meme Coins")
    console.print(table_new_meme_coins)
    html_new_meme_coins = console.export_html(inline_styles=True)
    with open("new_meme_coins.html", "w") as f:
        f.write(html_new_meme_coins)
