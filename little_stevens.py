import json
import os
import time
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from slugify import slugify

from abstract_podcast import AbstractPodcast
from get_driver import SeleniumDriver
from get_substack_audio import download_file
from mp3_tags import write_id3_tags_dict
from utils import download_file_requests_stream, create_filename_and_folders


def find_content_script(driver):
    all_scripts = driver.find_elements(By.TAG_NAME, 'script')
    for s in all_scripts:
        if s.get_attribute('outerHTML').find('window.CONTENT') >= 0:
            return s.get_attribute('innerHTML')
    return None


def build_json(inner_html):
    json_init = inner_html.find('{')
    json_end = inner_html.find('window.BACKUP_CONTENT')
    if 0 <= json_init < json_end:
        json_str = inner_html[json_init:json_end - 4]
        return json.loads(json_str)
    return None


class LittleStevensUndergroundGarage(AbstractPodcast):
    """
        Implements AbstractPodcast for the TabsOut.com podcast
    """

    def __init__(self, output_path=None):
        self.__output_path = output_path

    def check_url(self, url_to_check: str) -> bool:
        return urlparse(url_to_check).hostname.find('undergroundgarage') != -1

    def list_episodes(self, start_url: str) -> list:
        with SeleniumDriver(headless=False) as driver:
            driver.get(start_url)
            links = driver.find_elements(By.CSS_SELECTOR, 'div.slide a')
            return [x.get_attribute('href') for x in links]
        return []

    def get_episode(self, episode_url: str) -> bool:
        url_parsed = urlparse(episode_url)

        with SeleniumDriver(headless=False) as driver:
            date = driver.find_element(By.CLASS_NAME, 'entry-dateline-link').text
            time.sleep(3)
            driver.switch_to.frame(0)
            inner_html = find_content_script(driver)
            if not inner_html:
                return False
            json_dict = build_json(inner_html)
            if not json_dict:
                return False
            episode_name_slug = slugify(json_dict['data'][0]['author'])
            for item in json_dict['data']:
                try:
                    mp3_url = item['fileUrl']

                    mp3_file_name = create_filename_and_folders(output_dir=self.__output_path,
                                                               podcast_title=f"{episode_name_slug} - {item['title']}",
                                                               filename=episode_name_slug) + '.mp3'
                    episode_title = f"{episode_name_slug} - {item['title']}.mp3"
                    # mp3_file_name = os.path.join(output_path, episode_title)
                    download_file_requests_stream(file_url=mp3_url, file_name=mp3_file_name, block_size=100)

                    tag_dict = {
                        'artist': 'Little Stevens Underground Garage',
                        'album': f'Podcast Little Stevens Underground Garage',
                        'title': episode_title,
                        'date': date,
                        'website': url_parsed.netloc,
                        'genre': 'Podcast'
                    }
                    write_id3_tags_dict(mp3_file_name, art_filename=None, tag_dict=tag_dict)
                    return True
                except Exception as ex:
                    print(episode_url + ' FAILED')
        return False

    def set_output_path(self, output_path: str):
        self.__output_path = output_path

