import os
import re
import time

import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils import parse_retry

# Config
# Price increase ratio threshold (ignore everything higher than this ratio)
INCR_MAX = 0.2
# Telegram chat ID that receives update messages (could be a channel in @channel_id format)
# TG_RECEIVER = 1770239825
TG_RECEIVER = '@toronto_bestbuy_gpu'
# Telegram bot token
TG_TOKEN = os.environ['TG_TOKEN']

# Constants
CSS = By.CSS_SELECTOR
MODELS = [
    ['3060 ti', 400,  132],
    ['3070 ti', 600,  167],
    ['3080 ti', 1200, 233],
    ['3050',    250,  73],
    ['3060',    330,  98],
    ['3070',    500,  154],
    ['3080',    700,  204],
    ['3090',    1500, 236],
]
USD_TO_CAD = 1.27
AVAIL_TABLE: dict[str, bool] = {}
IGNORED = []
TITLE_SHORTEN = re.compile('(rtx|nvidia|geforce|edition|gddr[56]x*|video|card)', flags=re.IGNORECASE)


def shorten_title(title: str):
    short_title = TITLE_SHORTEN.sub('', title)
    while '  ' in short_title:
        short_title = short_title.replace('  ', ' ')
    return short_title.strip()


def send_message(msg: str):
    r = requests.get(f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
                     params={'chat_id': TG_RECEIVER, 'parse_mode': 'Markdown', 'text': msg})

    if r.status_code != 200:
        print('Request not OK:', r.status_code, r.text)


def parse_page(browser: Chrome):
    # Parse page
    for item in browser.find_elements(By.CLASS_NAME, 'x-productListItem'):
        title = item.find_element(CSS, 'div[data-automation="productItemName"]').get_attribute('innerHTML')
        title = shorten_title(title)

        # Ignored
        if title in IGNORED:
            continue

        # Check availability
        avail = item.find_elements(CSS, 'div[data-automation="store-availability-messages"] span[data-automation="store-availability-checkmark"]')

        # Not available, check if it was previously available
        if len(avail) == 0:
            if title in AVAIL_TABLE:
                send_message(f'Sold out: `{title}`')
                del AVAIL_TABLE[title]
            continue

        # Already sent availability message
        if title in AVAIL_TABLE:
            continue

        # Get price
        price = item.find_element(CSS, 'div[data-automation="product-pricing"] > span > div').get_attribute('innerHTML')
        price = round(float(price.replace(',', '')[1:]))
        price_usd = price / USD_TO_CAD

        # Find model
        lower = title.lower()
        model = [c for c in MODELS if c[0] in lower]
        if not model:
            continue
        model = model[0]

        # Calculate price increase
        price_incr = (price_usd - model[1]) / model[1]
        value = model[2] / price_usd * 100

        # Check incr threshold
        if price_incr > INCR_MAX:
            print(' '.join(title.split()[:2]), f'is in stock but price increase {price_incr * 100:.0f}% '
                                               f'is larger than defined threshold.')
            IGNORED.append(title)
            continue

        # Find link
        link = item.find_element(CSS, 'a').get_attribute('href')

        # Available and meets threshold criteria, notify user
        AVAIL_TABLE[title] = True
        send_message(f'{model[0].upper()} Became Available!\n'
                     f'\n'
                     f'${price:.0f} | {price_incr * 100:.0f}% Incr | Value: {value:.0f}\n'
                     f'- [{title}]({link})')


if __name__ == '__main__':
    web_options = Options()
    # web_options.headless = True

    browser = Chrome(options=web_options)
    # browser.get('https://www.bestbuy.ca/en-ca/collection/graphics-cards-with-nvidia-chipset/349221')
    browser.get('https://www.bestbuy.ca/en-ca/collection/rtx-30-series-graphic-cards/316108')

    # parse_page(browser)
    # browser.close()

    # Refresh indefinitely
    while True:
        time.sleep(5)
        parse_retry(parse_page, browser)
        browser.refresh()
        time.sleep(2)
