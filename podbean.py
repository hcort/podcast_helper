"""
    Podbean has a website that can be crawled and a RSS feed with direct links to each epidose
"""
import json
import time
from urllib.parse import urlparse

import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from abstract_podcast import AbstractPodcast
from get_driver import get_driver, hijack_cookies
from utils import create_filename_and_folders
from mp3_tags import write_mp3_tags


class PodbeanPodcast(AbstractPodcast):

    def __init__(self, output_path=None):
        self.__output_path = output_path

    def check_url(self, url_to_check: str) -> bool:
        return urlparse(url_to_check).hostname.find('podbean') != -1

    def list_episodes(self, start_url: str) -> list:
        return get_episode_list(start_url)

    def get_episode(self, episode_url: str) -> bool:
        return get_episode(output_path=self.__output_path, episode_url=episode_url)

    def set_output_path(self, output_path: str):
        self.__output_path = output_path


def get_episode_cover_art(driver, output_dir, podcast_title):
    try:
        img_tag = driver.find_element(By.CSS_SELECTOR, 'div.e-logo>img')
        img_url = img_tag.get_attribute('src')
        img_req = requests.get(img_url, timeout=30)
        img_filename = create_filename_and_folders(output_dir, podcast_title, img_url)
        ext_sep = img_filename.rfind('-', len(img_filename) - 5, len(img_filename))
        img_filename = img_filename[:ext_sep - 1] + '.' + img_filename[ext_sep + 1:]
        with open(img_filename, mode='wb') as localfile:
            localfile.write(img_req.content)
    except Exception as err:
        print(f'Error downloading cover art - {driver.title} - {err}')
        img_filename = ''
    return img_filename


def get_episode(episode, output_dir):
    driver = get_driver()
    if not episode or not driver:
        return None
    driver.get(episode)
    try:
        time.sleep(5)
        podcast_json_data = driver.find_elements(By.TAG_NAME, 'script')[3].get_attribute('innerHTML')
        json_dict = json.loads(podcast_json_data)
        episode_title = json_dict['name']
        episode_autor = json_dict['partOfSeries']['name']
        # episode_description = json_dict['description']
        episode_date = json_dict['datePublished']
        episode_mp3_url = json_dict['associatedMedia']['contentUrl']
        image_filename = get_episode_cover_art(driver, output_dir, episode_autor)
        # download file using requests
        requests_session = hijack_cookies(driver)
        redirected = requests_session.get(episode_mp3_url)
        mp3_filename = create_filename_and_folders(output_dir, episode_autor, episode_title) + '.mp3'
        with open(mp3_filename, mode='wb') as localfile:
            localfile.write(redirected.content)
        write_mp3_tags(episode_title, episode_autor, episode_date, image_filename, mp3_filename)
    except Exception as err:
        print(f'{episode} - {driver.title} - {err}')


def get_episode_list(podcast):
    driver = get_driver()
    if not podcast or not driver:
        return None
    driver.get(podcast)
    episode_list = []
    timeout = 5
    try:
        load_more_link = driver.find_element(By.LINK_TEXT, 'Load more')
        while load_more_link:
            driver.execute_script('arguments[0].click();', load_more_link)
            # when clicking "load more" a spinner appears and then disappears
            WebDriverWait(driver, timeout).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, 'spinner-border')))
            WebDriverWait(driver, timeout).until_not(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, 'spinner-border')))
            try:
                load_more_link = driver.find_element(By.LINK_TEXT, 'Load more')
            except NoSuchElementException:
                load_more_link = None
        all_links = driver.find_elements(By.CSS_SELECTOR, 'h2.card-title>a')
        episode_list = [x.get_attribute('href') for x in all_links]
    except Exception as err:
        print(f'{podcast} - Error getting episode list: {err}')
    return episode_list

