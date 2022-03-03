from __future__ import annotations

import traceback
from typing import Callable, Optional

import requests
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


CSS = By.CSS_SELECTOR


def parse_retry(parser: Callable, browser: WebDriver, tries: int = 0):
    try:
        parser(browser)
    except StaleElementReferenceException:
        if tries < 3:
            parse_retry(parser, browser, tries + 1)
    except Exception as e:
        traceback.print_exc()


class TelegramReporter:
    token: str
    receiver: str | int
    alert_receiver: Optional[str | int]

    def __init__(self, token: str, receiver: str, alert_receiver: Optional[str | int]):
        self.token = token
        self.receiver = receiver
        self.alert_receiver = alert_receiver

    def send(self, msg: str, rec: Optional[str | int] = None) -> bool:
        """
        Send a message

        :param msg: Message string
        :param rec: Receiver
        :return: Success or not
        """
        if rec is None:
            rec = self.receiver

        r = requests.get(f'https://api.telegram.org/bot{self.token}/sendMessage',
                         params={'chat_id': rec, 'parse_mode': 'Markdown', 'text': msg})

        if r.status_code != 200:
            print('Request not OK:', r.status_code, r.text)

        return r.status_code == 200

    def alert(self) -> bool:
        if self.alert_receiver:
            return self.send('/alert', self.alert_receiver)
