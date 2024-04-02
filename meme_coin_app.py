from flask import Flask, render_template_string
from flask_apscheduler import APScheduler
from new_meme_tracing import report_coins
import os

lunarcrush_api_key = os.getenv('LUNARCRUSH_API_KEY')

app = Flask(__name__)

# Configure APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@scheduler.task('interval', id='fetch_meme_coins', seconds=30)
def scheduled_coin_job():
    print("Scheduler triggered every 30 seconds")
    report_coins(lunarcrush_api_key)


@app.route('/')
def index():
    with open('meme_coins.html', 'r') as f:
        meme_coins_html = f.read()

    with open('new_meme_coins.html', 'r') as f:
        new_meme_coins_html = f.read()

    html_content = f'''
        <h1>Meme Coins</h1>
        <div>
            <h2>All Meme Coins</h2>
            {meme_coins_html}
        </div>
        <hr>
        <div>
            <h2>New Meme Coins</h2>
            {new_meme_coins_html}
        </div>
    '''

    return render_template_string(html_content)


if __name__== '__main__':
    app.run()
