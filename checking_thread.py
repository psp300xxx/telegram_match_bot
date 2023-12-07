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

    def run(self) -> None:
        self.driver.get(self.url)
        while not self.condition(self.match, self.driver):
            print("Checking")
            self.delegate.on_condition_not_accepted()
            time.sleep(10)
            self.driver.get(self.url)
        self.delegate.on_condition_accepted()
        self.driver.close()

