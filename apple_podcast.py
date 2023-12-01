import json
import time
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from abstract_podcast import AbstractPodcast
from get_driver import get_driver, hijack_cookies
from utils import create_filename_and_folders
from mp3_tags import write_mp3_tags

podcast_json_id = 'shoebox-media-api-cache-amp-podcasts'


class ApplePodcast(AbstractPodcast):

    def __init__(self, output_path=None):
        self.__output_path = output_path

    def check_url(self, url_to_check: str) -> bool:
        return urlparse(url_to_check).hostname.find('apple') != -1

    def list_episodes(self, start_url: str) -> list:
        return get_all_episodes(start_url)

    def get_episode(self, episode_url: str) -> bool:
        return get_episode(output_path=self.__output_path, episode_url=episode_url)

    def set_output_path(self, output_path: str):
        self.__output_path = output_path


def get_all_episodes(start_url):
    # div.list-button button.link
    driver = get_driver()
    timeout = 10
    all_podcast_links = []
    try:
        keep_scrolling = True
        driver.get(start_url)
        while keep_scrolling:
            try:
                # scroll_element = driver.find_element(By.CLASS_NAME, "visibility-check")
                try:
                    more_episodes_button_presence = EC.presence_of_element_located(
                        (By.ID, "didomi-notice-agree-button"))
                    WebDriverWait(driver, timeout).until(more_episodes_button_presence)
                except TimeoutException:
                    keep_scrolling = False
                button = driver.find_element(By.CSS_SELECTOR, 'div.list-button button.link')
                button.click()
                time.sleep(2)
            except NoSuchElementException:
                keep_scrolling = False
        all_podcast_entries = driver.find_elements(By.CSS_SELECTOR, 'ol.tracks a.link')
        all_podcast_links = [item.get_attribute('href') for item in all_podcast_entries]
    except TimeoutException as ex:
        print(f'Error accessing {start_url}: Timeout: {ex}')
    finally:
        driver.close()
    return all_podcast_links


def get_episode(episode, output_dir):
    driver = get_driver()
    if not episode or not driver:
        return None
    driver.get(episode)
    try:
        podcast_json_data = driver.find_element(By.ID, podcast_json_id).get_attribute('innerHTML')
        json_dict = json.loads(podcast_json_data)
        json_dict = json.loads(json_dict[list(json_dict.keys())[0]])
        episode_title = json_dict['d'][0]['attributes']['name']
        episode_autor = json_dict['d'][0]['attributes']['artistName']
        episode_date = json_dict['d'][0]['attributes']['releaseDateTime']
        episode_mp3_url = json_dict['d'][0]['attributes']['assetUrl']
        image_filename = driver.find_element(By.CLASS_NAME, 'we-artwork__image').get_attribute('src')
        requests_session = hijack_cookies(driver)
        redirected = requests_session.get(episode_mp3_url)
        mp3_filename = create_filename_and_folders(output_dir, episode_autor, episode_title) + '.mp3'
        with open(mp3_filename, mode='wb') as localfile:
            localfile.write(redirected.content)
        write_mp3_tags(episode_title, episode_autor, episode_date, image_filename, mp3_filename)
    except Exception as err:
        print(f'{episode} - {driver.title} - {err}')

