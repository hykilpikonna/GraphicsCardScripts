import math
from dataclasses import dataclass
from html import unescape
from urllib.parse import unquote

import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from utils import CSS


@dataclass()
class AvailableStore:
    loc: str
    avail: str
    n: int


@dataclass()
class AvailableStoreV2(AvailableStore):
    loc_key: str
    fulfillment_key: str


def get_avail_v2(url: str, postal='M5H1N1') -> list[AvailableStore]:
    sku = int(url.split('/')[-1])
    params = {
        'accept': 'application/vnd.bestbuy.standardproduct.v1+json',
        'accept-language': 'en-CA',
        'locations': '977|203|931|62|617|927|965|57|938|237|943|932|956|202|200|937|926|795|916|233|544|910|954|207|930|622|223|245|925|985|990|959|949|942',
        'postalCode': postal,
        'skus': sku
    }

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
        "referer": url,
    }

    r = requests.get('https://www.bestbuy.ca/ecomm-api/availability/products', params=params, headers=headers)
    o = r.json()['availabilities'][0]['pickup']['locations']
    return [AvailableStoreV2(loc['name'], str(loc['quantityOnHand']), loc['quantityOnHand'], loc['locationKey'], loc['fulfillmentKey'])
            for loc in o if loc['quantityOnHand'] > 0]


def get_availability(browser: WebDriver, url: str) -> list[AvailableStore]:
    browser.get(url)

    # Get stores element
    stores = browser.find_elements(CSS, '.x-nearby-stores > *')

    # Filter stores, not 'check other stores' button
    stores = [s for s in stores if not s.get_attribute('data-automation')]

    # Filter stores that are available
    stores = [s for s in stores if len(s.find_elements(CSS, '[data-automation="store-availability-checkmark"]'))]

    if not stores:
        return []

    # Get availability
    result = []
    for store in stores:
        loc = unescape(store.find_element(CSS, '[data-automation="pickup-store-list-item-store-name"]').get_attribute('innerHTML').strip())
        avail = store.find_elements(By.XPATH, './/*[@data-automation="pickup-store-list-item-reserve-button"]/following-sibling::span/following-sibling::span')

        if not avail:
            avail = 'Available'
            n = 100
        else:
            avail = unescape(avail[0].get_attribute('innerHTML').strip())
            n = [int(s) for s in avail.split() if s.isdigit()][0]

        result.append(AvailableStore(loc, avail, n))

    return result

