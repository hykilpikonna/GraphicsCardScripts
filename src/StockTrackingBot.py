import os
import time

import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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


def parse_page(browser: Chrome):
    # Parse page
    for item in browser.find_elements(By.CLASS_NAME, 'x-productListItem'):
        title = item.find_element(CSS, 'div[data-automation="productItemName"]').get_attribute('innerHTML')

        # Check availability
        avail = item.find_elements(CSS, 'div[data-automation="store-availability-messages"] span[data-automation="store-availability-checkmark"]')

        # Not available, check if it was previously available
        if len(avail) == 0:
            if title in AVAIL_TABLE:
                # TODO: Feedback
                del AVAIL_TABLE[title]
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
            continue

        # Available and meets threshold criteria, notify user
        AVAIL_TABLE[title] = True

        print(model)
        print(title)


if __name__ == '__main__':
    web_options = Options()
    # web_options.headless = True

    browser = Chrome(options=web_options)
    browser.get('https://www.bestbuy.ca/en-ca/collection/graphics-cards-with-nvidia-chipset/349221')

    parse_page(browser)
    browser.close()

    # Refresh indefinitely
    # while True:
    #     parse_page(browser)
    #     time.sleep(5)
    #     browser.refresh()
