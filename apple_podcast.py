"""
    Used to download podcasts from Apple podcast
"""
import json
import time
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from abstract_podcast import AbstractPodcast
from get_driver import get_driver, hijack_cookies
from utils import create_filename_and_folders, get_file_requests
from mp3_tags import write_mp3_tags

podcast_json_id = 'shoebox-media-api-cache-amp-podcasts'


class ApplePodcast(AbstractPodcast):
    """
        Implements AbstractPodcast interface for podcasts hosted in the Apple platform
    """

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


current_scroll_script = 'var current_scroll=window.scrollY;return current_scroll;'
max_scroll_script = 'var max_scroll=document.body.scrollHeight;return max_scroll;'
scroll_to_x_script = 'window.scrollTo(0, {});var current_scroll=document.body.scrollHeight;return current_scroll;'
scroll_script = 'window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;'


def keep_scrolling_loop(driver):
    try:
        num_sections = -1
        old_num_sections = 0
        while (num_sections != 0) and (num_sections != old_num_sections):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(1)
            old_num_sections = num_sections
            num_sections = len(driver.find_elements(By.TAG_NAME, 'section'))
    except Exception as err:
        import traceback
        print(traceback.format_exc())
        print(err)
    return False


def get_all_episodes(start_url):
    # div.list-button button.link
    driver = get_driver()
    timeout = 10
    all_podcast_links = []
    see_more_button_clicked = False
    try:
        keep_scrolling = True
        driver.get(start_url)
        while keep_scrolling:
            if not see_more_button_clicked:
                try:
                    button = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="link-list"] > a[data-testid="click-action"]')
                    button.click()
                    time.sleep(2)
                except NoSuchElementException:
                    keep_scrolling = False
            # cargados todos los episodios
            keep_scrolling = keep_scrolling_loop(driver)
        all_podcast_entries = driver.find_elements(By.CSS_SELECTOR, 'ol[data-testid="episodes-list"] a.link-action')
        all_podcast_links = [item.get_attribute('href') for item in all_podcast_entries]
    except TimeoutException as ex:
        print(f'Error accessing {start_url}: Timeout: {ex}')
    # finally:
    #     driver.close()
    return all_podcast_links


def get_episode(episode_url, output_path):
    driver = get_driver()


    if not episode_url or not driver:
        return False
    driver.get(episode_url)
    try:
        try:
            # podcast data no longer in HTML
            play_button = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="button-icon-play"]')
            play_button.click()
            timeout = 50
            pause_button_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid="button-icon-pause"]'))
            WebDriverWait(driver, timeout).until(pause_button_present)
            pause_button = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="button-icon-pause"]')
            pause_button.click()
        except TimeoutException as ex:
            print(f'Error clicking play/pause button {episode_url} - {ex}')
            return False
        audio = driver.find_element(By.TAG_NAME, 'audio')
        episode_mp3_url = audio.get_attribute('src')
        js = driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
        json_dict = None
        for json_data in js:
            if json_data.get_attribute('innerHTML').find('\"@type\":\"PodcastEpisode\"') >= 0:
                json_dict = json.loads(json_data.get_attribute('innerHTML'))
        if not json_dict:
            print(f'Episode info not found {episode_url}')
            return False
        episode_title = json_dict['name']
        episode_autor = json_dict['partOfSeries']['name']
        episode_date = json_dict['datePublished']
        requests_session = hijack_cookies(driver)
        mp3_filename = create_filename_and_folders(output_path, episode_autor, episode_title) + '.mp3'
        get_file_requests(requests_session, episode_mp3_url, mp3_filename)
        write_mp3_tags(episode_title, episode_autor, episode_date, '', mp3_filename)
        return True
    except Exception as err:
        print(f'{episode_url} - {driver.title} - {err}')
    return False

