# This is a sample Python script.
import os.path
import threading
import time
from threading import Lock, RLock
import asyncio

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.service import Service

import checking_thread

import telegram
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from selenium import webdriver
import json
TELEGRAM_TOKEN = "6528189438:AAFYNfbhtrnrFFyVms2mNRgXSTDP0rFNmBg"

SALERNITANA_LINK = "https://salernitana.it/biglietteria/"
MATCH = "Salernitana - Milan"

driver: webdriver = None

MAIN_THREAD_LOOP = asyncio.get_event_loop()

INFO_JSON_PATH = "./users_info.json"


class DelegateImpl(checking_thread.UpdateDelegate):

    def __init__(self):
        self.user_ids: set = set()
        self.__load_stored_users__()
        self.lock: Lock = RLock()

    def __load_stored_users__(self):
        if not os.path.exists(INFO_JSON_PATH):
            return
        with open(INFO_JSON_PATH) as f:
            data = json.load(f)
            users = data["users"]
            for u in users:
                self.user_ids.add(u)

    def add_user_id(self, user_id: str):
        self.lock.acquire()
        self.user_ids.add(user_id)
        user_list: list = list(self.user_ids)
        self.lock.release()
        with open(INFO_JSON_PATH, "w") as f:
            res = {"users" : user_list}
            json.dump(res, f, indent=4)

    def on_condition_accepted(self):
        self.lock.acquire()
        for id in self.user_ids:
            loop = MAIN_THREAD_LOOP
            loop.create_task( app.updater.bot.send_message(id, "Match tickets are available at '{}'".format(SALERNITANA_LINK)) )
        self.lock.release()


    def on_condition_not_accepted(self):
        self.lock.acquire()
        for id in self.user_ids:
            loop = MAIN_THREAD_LOOP
            loop.create_task( app.updater.bot.send_message(id, "Match tickets are  not available at '{}'".format(SALERNITANA_LINK)) )
        self.lock.release()


DELEGATE = DelegateImpl()

def get_driver() -> webdriver:
    global driver
    if driver is None:
        opts = webdriver.firefox.options.Options()
        opts.add_argument("--headless")
        service = Service(executable_path='./geckodriver')
        driver = webdriver.Firefox(service=service,options=opts)
        print("driver created")
    return driver

def add_to_users(user):
    global DELEGATE
    DELEGATE.add_user_id(user_id=user)

def link_available(value: str, driver: webdriver) -> bool:
    elements = driver.find_elements(by=By.TAG_NAME, value="strong")
    for el in elements:
        if value in el.text:
            return True
    return False

async def notify_users(users: list, msg: str):
    if users is None:
        return
    for user in users:
        await user.send_message(msg)

def check_match_availability(driver: webdriver, match: str) -> bool:
    return link_available(value=match, driver=driver)



async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_to_users( update.effective_user.id )
    await update.message.reply_text("You have been inserted in queue, users are: '{}'".format(len(DELEGATE.user_ids)))



app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("hello", hello))

app.add_handler(CommandHandler("check", check))



thread = checking_thread.UpdateChecker(match=MATCH, url=SALERNITANA_LINK, condition=link_available, driver=get_driver(), delegate=DELEGATE)

print("thread object created")

thread.start()

# asyncio.run(check_match_availability(MATCH, SALERNITANA_LINK, users))

print("Running")

app.run_polling()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
