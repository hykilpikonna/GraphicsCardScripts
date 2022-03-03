from __future__ import annotations

import os
import time
import traceback
from typing import Callable, Optional

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from telegram import Bot, Message

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
    bot: Bot
    receiver: str | int
    alert_receiver: Optional[str | int]

    def __init__(self, token: str, receiver: str | int, alert_receiver: Optional[str | int]):
        self.bot = Bot(token)
        self.receiver = receiver
        self.alert_receiver = alert_receiver

    def send(self, msg: str, rec: Optional[str | int] = None) -> Message:
        """
        Send a message

        :param msg: Message string
        :param rec: Receiver
        :return: Edit code or None if failed
        """
        if rec is None:
            rec = self.receiver

        return self.bot.send_message(chat_id=rec, parse_mode='Markdown', text=msg)

    def alert(self) -> Message:
        if self.alert_receiver:
            return self.send('/alert', self.alert_receiver)
