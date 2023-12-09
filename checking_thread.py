import threading
import time
from typing import Callable

from selenium.webdriver.firefox import webdriver

class UpdateDelegate(object):

    def on_condition_accepted(self):
        pass


    def on_condition_not_accepted(self):
        pass



class UpdateChecker(threading.Thread):

    def __init__(self, match: str, url: str, condition: Callable, driver: webdriver, delegate: UpdateDelegate = None, *args, **kwargs):
        super(UpdateChecker, self).__init__()
        self.match : str = match
        self.url : str = url
        self.condition : Callable[[webdriver, str], bool] = condition
        self.driver = driver
        self.delegate = delegate

    def _driver_get(self):
        done = False
        attempts = 30
        exception: Exception = None
        while not done and attempts > 0:
            try:
                self.driver.get(self.url)
                done = True
            except Exception as exc:
                exception = exc
                attempts -= 1
                done = False
        if attempts <= 0:
            raise RuntimeError("Unable to connect due to: '{}'".format(str(exception)))

    def run(self) -> None:
        self.driver.get(self.url)
        print("Starting selenium")
        while not self.condition(self.match, self.driver):
            self.delegate.on_condition_not_accepted()
            time.sleep(10)
            self._driver_get()
        self.delegate.on_condition_accepted()
        self.driver.close()

