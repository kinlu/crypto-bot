import asyncio
from datetime import datetime

from flask import Flask, render_template_string
from flask_apscheduler import APScheduler

from interface.discord_messager import send_discord_message
from new_meme_tracing import report_coins
import os

lunarcrush_api_key = os.getenv('LUNARCRUSH_API_KEY')
discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')
discord_channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
railway_public_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')

app = Flask(__name__)

# Configure APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


def scheduled_coin_job():
    print("Scheduler triggered...")

    # Clean up the files in the "htmls" folder
    print("Cleaning up HTML files...")
    html_directory = 'htmls'
    for filename in os.listdir(html_directory):
        if filename.startswith('coins_') and filename.endswith('.html'):
            file_path = os.path.join(html_directory, filename)
            os.remove(file_path)
    print("Regenerating HTML files...")
    report_coins(lunarcrush_api_key, discord_bot_token, discord_channel_id)
    message = f"For detail, visit https://{railway_public_domain}/"
    asyncio.run(send_discord_message(discord_bot_token, discord_channel_id, message))


# Schedule the job to run immediately and then every 30 minutes
scheduler.add_job(id='fetch_coins', func=scheduled_coin_job, trigger='interval', minutes=60, next_run_time=datetime.now())


@app.route('/')
def index():
    html_content = '<h1>Coin Categories</h1>'

    # Specify the directory path for the HTML files
    html_directory = 'htmls'

    # Iterate over all HTML files in the specified directory
    for filename in os.listdir(html_directory):
        if filename.startswith('coins_') and filename.endswith('.html'):
            file_path = os.path.join(html_directory, filename)
            with open(file_path, 'r') as f:
                category_html = f.read()

            category_name = filename[6:-5].capitalize()  # Extract the category name from the filename

            html_content += f'''
                <div>
                    <h2>{category_name} Coins</h2>
                    {category_html}
                </div>
                <hr>
            '''

    return render_template_string(html_content)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.getenv("PORT", default=5000))
