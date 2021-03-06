import os
import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils import parse_retry, TelegramReporter, CSS

# Config
# Telegram chat ID that receives update messages (could be a channel in @channel_id format)
# TG_RECEIVER = 1770239825
TG_RECEIVER = '@toronto_ps5_bestbuy'
# Telegram bot token
TG_TOKEN = os.environ['TG_TOKEN']
# Alert receiver telegram chat ID
ALERT_RECEIVER = -1001655384423

# Constants
AVAIL_TABLE: dict[str, bool] = {}
TG = TelegramReporter(TG_TOKEN, TG_RECEIVER, ALERT_RECEIVER)


def parse_page(browser: Chrome):
    # Parse page
    for item in browser.find_elements(By.CLASS_NAME, 'x-productListItem'):
        title = item.find_element(CSS, 'div[data-automation="productItemName"]').get_attribute('innerHTML')

        # Check availability
        avail = item.find_elements(CSS, 'div[data-automation="store-availability-messages"] span[data-automation="store-availability-checkmark"]')

        # Not available, check if it was previously available
        if len(avail) == 0:
            if title in AVAIL_TABLE:
                TG.send(f'Sold out: `{title}`')
                del AVAIL_TABLE[title]
            continue

        # Already sent availability message
        if title in AVAIL_TABLE:
            continue

        # Get price
        price = item.find_element(CSS, 'div[data-automation="product-pricing"] > span > div').get_attribute('innerHTML')
        price = round(float(price.replace(',', '')[1:]))

        # Find link
        link = item.find_element(CSS, 'a').get_attribute('href')

        # Available and meets threshold criteria, notify user
        AVAIL_TABLE[title] = True
        TG.send(f'PS5 Became Available!\n'
                        f'- [{title}]({link}) ${price:.2f}')

        # Check alert
        TG.alert()


if __name__ == '__main__':
    web_options = Options()
    # web_options.headless = True

    browser = Chrome(options=web_options)
    browser.get('https://www.bestbuy.ca/en-ca/category/ps5-consoles/17583383')

    TG.send('Bot restarted')

    # parse_page(browser)
    # browser.close()

    # Refresh indefinitely
    while True:
        time.sleep(5)
        parse_retry(parse_page, browser)
        browser.refresh()
        time.sleep(2)
