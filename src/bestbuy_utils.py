import math
from dataclasses import dataclass
from html import unescape
from urllib.parse import unquote

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from utils import CSS


@dataclass
class AvailableStore:
    loc: str
    avail: str
    n: int


def get_availability(browser: WebDriver, url: str):
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
        avail = store.find_elements(By.XPATH, '//*[@data-automation="pickup-store-list-item-reserve-button"]/following-sibling::span/following-sibling::span')

        if not avail:
            avail = 'Available'
            n = 100
        else:
            avail = unescape(avail[0].get_attribute('innerHTML').strip())
            n = [int(s) for s in avail.split() if s.isdigit()][0]

        result.append(AvailableStore(loc, avail, n))

    return result

