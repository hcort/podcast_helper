import os

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def hijack_cookies(driver):
    cookies = driver.get_cookies()
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 "
            "Safari/537.36 "
    }
    s = requests.session()
    s.headers.update(headers)
    for cookie in cookies:
        # s.cookies.set_cookie(cookie)
        s.cookies.set(cookie['name'], cookie['value'])
    return s



def get_driver():
    # os.environ['MOZ_HEADLESS'] = '1'
    firefox_loc = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    options = Options()
    options.binary_location = firefox_loc
    return webdriver.Firefox(options=options)
