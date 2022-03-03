import traceback
from typing import Callable

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver


def parse_retry(parser: Callable, browser: WebDriver, tries: int = 0):
    try:
        parser(browser)
    except StaleElementReferenceException:
        if tries < 3:
            parse_retry(parser, browser, tries + 1)
    except Exception as e:
        traceback.print_exc()
