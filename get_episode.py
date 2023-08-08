import os

import requests
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from slugify import slugify

from get_driver import hijack_cookies, get_driver
from mp3_tags import write_mp3_tags


def set_headers(requests_session, referer_url):
    headers = {
            'authority': 'www.ivoox.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'referer': referer_url,
            'sec-ch-ua': '\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '\"Windows\"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1'
        }
    requests_session.headers.update(headers)
    return requests_session


def create_filename_and_folders(output_dir, podcast_title, filename):
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), output_dir)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    dir_path = os.path.join(dir_path, podcast_title)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return os.path.join(dir_path, slugify(filename, max_length=200))


def get_episode_cover_art(driver, output_dir, podcast_title):
    img_tag = driver.find_element(By.CLASS_NAME, 'main.lozad.elevate-2')
    img_url = img_tag.get_attribute('src')
    img_req = requests.get(img_url)
    img_filename = create_filename_and_folders(output_dir, podcast_title, img_url)
    ext_sep = img_filename.rfind('-', len(img_filename) - 5, len(img_filename))
    img_filename = img_filename[:ext_sep - 1] + '.' + img_filename[ext_sep + 1:]
    with open(img_filename, mode='wb') as localfile:
        localfile.write(img_req.content)
    return img_filename


def get_episode(driver=None, episode='', output_dir=''):
    timeout = 5
    if not episode or not driver:
        return None
    driver.get(episode)
    try:
        cookie_button_present = EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
        WebDriverWait(driver, timeout).until(cookie_button_present)
        cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
        cookie_button.click()
        WebDriverWait(driver, timeout).until_not(cookie_button_present)
    except TimeoutException as ex:
        # cookies already accepted
        print(f'Error clicking cookies button {episode}')
    download_buttons = driver.find_elements(By.ID, "lnk_download")
    # driver.execute_script("arguments[0].scrollIntoView(true);", download_buttons[1])
    download_buttons[1].click()
    try:
        next_page_present = EC.presence_of_element_located((By.CLASS_NAME, "downloadlink.displaynone"))
        WebDriverWait(driver, timeout).until(next_page_present)
        download_links_container = driver.find_element(By.CLASS_NAME, "downloadlink.displaynone")
        download_links = download_links_container.find_elements(By.TAG_NAME, "a")
        requests_session = hijack_cookies(driver)
        requests_session = set_headers(requests_session, download_links[0].get_attribute('href'))
        redirected = requests_session.get(download_links[0].get_attribute('href'))
        mp3_filename_end = redirected.url.find('.mp3')
        mp3_filename_start = redirected.url.rfind('/', 0, mp3_filename_end)
        mp3_filename = redirected.url[mp3_filename_start+1:mp3_filename_end+4]
        podcast_title = driver.find_element(By.CLASS_NAME, 'normal').get_attribute('title')
        podcast_date = driver.find_element(By.CLASS_NAME, 'icon-date').text
        episode_title = driver.find_element(By.TAG_NAME, 'h1').text
        mp3_filename = create_filename_and_folders(output_dir, podcast_title, episode_title) + '.mp3'
        with open(mp3_filename, mode='wb') as localfile:
            localfile.write(redirected.content)
        image_filename = get_episode_cover_art(driver, output_dir, podcast_title)
        write_mp3_tags(episode_title, podcast_title, podcast_date, image_filename, mp3_filename)
    except TimeoutException as ex:
        # cookies already accepted
        print(f'Could not download episode {episode} - {ex}')
    except Exception as ex:
        print(f'Could not download episode {episode} - {ex}')


def get_all_episodes(driver=None, episode_list=[]):
    if not episode_list or not driver:
        return None
    for episode in episode_list:
        get_episode(driver, episode)


def get_ivoox_episode(output_path, episode_url):
    driver = get_driver()
    get_episode(driver=driver, episode=episode_url, output_dir=output_path)
