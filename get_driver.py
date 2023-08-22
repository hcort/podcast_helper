import os
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service


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
        print(f"{cookie['name']}: {cookie['value']}")
        s.cookies.set(cookie['name'], cookie['value'])
    return s


def get_driver():
    # os.environ['MOZ_HEADLESS'] = '1'
    firefox_loc = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    # options = webdriver.FirefoxOptions()
    # options.binary_location = firefox_loc
    # return webdriver.Firefox(options=options)
    service = Service(executable_path=firefox_loc)
    return webdriver.Chrome(service=service)


def get_driver_opera(opera_exe_location, opera_preferences_location):
    # use custom preferences file to change the download folder
    from selenium.webdriver.opera.options import Options
    opera_options = Options()
    opera_options.binary_location = opera_exe_location
    opera_options.add_argument(f'user-data-dir={opera_preferences_location}')
    return webdriver.Opera(options=opera_options)
