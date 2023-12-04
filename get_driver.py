"""
    get_driver is used to build a Selenium Firefox driver

    get_drive_opera is used to build a Selenium Opera driver
        Opera seems to be deprecated as a driver in more recent Selenium versions
        Opera is used to access webpages via the built-in VPN

    hijack_cookies is used to get the actual cookies from the driver and inject
    them into a Requests session
"""
import os.path
import shutil

import requests
from selenium import webdriver
# from selenium.webdriver.opera.options import Options
from sys import platform

from selenium.webdriver.firefox.service import Service

from utils import read_config_object

global_selenium_driver = None


def geckodriver_name():
    if platform == 'win32':
        return 'geckodriver.exe'
    else:
        return 'geckodriver'


def firefox_location():
    if platform == 'win32':
        return read_config_object()['firefox_location']['windows']
    else:
        return read_config_object()['firefox_location']['linux']


def hijack_cookies(driver):
    cookies = driver.get_cookies()
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 '
            'Safari/537.36 '
    }
    s = requests.session()
    s.headers.update(headers)
    for cookie in cookies:
        # s.cookies.set_cookie(cookie)
        s.cookies.set(cookie['name'], cookie['value'])
    return s


def get_driver():
    global global_selenium_driver
    if not global_selenium_driver:
        os.environ['MOZ_HEADLESS'] = '1'
        firefox_loc = firefox_location()
        print(firefox_loc)
        geckodriver_path = os.path.join(os.getcwd(), os.path.join('res', geckodriver_name()))
        shutil.copy(geckodriver_path, os.getcwd())
        # service = Service(executable_path=firefox_loc)
        # return webdriver.Firefox(service=service)
        options = webdriver.FirefoxOptions()
        options.binary_location = firefox_loc
        # return webdriver.Firefox(timeout=30, firefox_options=options)
        log_path = os.path.join(os.path.join(os.getcwd(), 'log'), os.path.join('log', 'geckodriver.log'))
        service = Service(log_path=log_path)
        global_selenium_driver = webdriver.Firefox(service=service)
    return global_selenium_driver


def close_and_remove_driver():
    if global_selenium_driver:
        global_selenium_driver.quit()
        os.remove(os.path.join(os.getcwd(), os.path.join('res', geckodriver_name())))


def get_driver_opera(opera_exe_location, opera_preferences_location):
    # use custom preferences file to change the download folder
    opera_options = webdriver.opera.options.Options()
    opera_options.binary_location = opera_exe_location
    opera_options.add_argument(f'user-data-dir={opera_preferences_location}')
    return webdriver.Opera(options=opera_options)
