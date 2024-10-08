"""
    Used to download podcasts from substack
"""
import json
import os
import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from slugify import slugify

from abstract_podcast import AbstractPodcast
from import_selenium_cond import Keys
from mp3_tags import write_id3_tags_dict
from utils import download_file_requests_stream


class SubstackPodcast(AbstractPodcast):
    """
        Implements AbstractPodcast interface for podcasts hosted in the substack platform
    """

    def __init__(self, output_path=None):
        self.__output_path = output_path

    def check_url(self, url_to_check: str) -> bool:
        return urlparse(url_to_check).hostname.find('substack') != -1

    def list_episodes(self, start_url: str) -> list:
        return list_all_podcasts(start_url)

    def get_episode(self, episode_url: str) -> bool:
        return get_substack_episode(output_path=self.__output_path, episode_url=episode_url)

    def set_output_path(self, output_path: str):
        self.__output_path = output_path


def download_file(output_path, link, name):
    filename = os.path.join(output_path, name)
    if not os.path.exists(filename):
        download_file_requests_stream(link, filename, block_size=64)
    return filename


def list_all_podcasts(substack_link):
    url_parsed = urlparse(substack_link)
    archive_url = f'https://{url_parsed.netloc}/archive'
    all_podcast_links = []
    driver = webdriver.Firefox()
    try:
        keep_scrolling = True
        driver.get(archive_url)
        while keep_scrolling:
            try:
                # scroll_element = driver.find_element(By.CLASS_NAME, "visibility-check")
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(2)
            except NoSuchElementException:
                keep_scrolling = False
        all_podcast_entries = driver.find_elements(By.CSS_SELECTOR, 'a.podcast')
        all_podcast_links = [item.get_attribute('href') for item in all_podcast_entries]
    except TimeoutException as ex:
        print(f'Error accessing {substack_link}: Timeout: {ex}')
    finally:
        driver.close()
    return all_podcast_links


def get_substack_episode(output_path, episode_url):
    os.environ['MOZ_HEADLESS'] = '1'
    driver = webdriver.Firefox()
    url_parsed = urlparse(episode_url)
    try:
        # div.single-post article div div.container audio
        driver.get(episode_url)
        elements = driver.find_elements(By.TAG_NAME, 'audio')
        mp3_url = elements[0].get_attribute('src') if (len(elements) > 0) else ''
        if not mp3_url:
            print(f'Error reading {episode_url}: No audio found.')
            return

        json_str = driver.find_element(By.CSS_SELECTOR, 'div#main script:nth-of-type(2)').get_attribute('innerHTML')
        json_data = json.loads(json_str)
        episode_title = json_data['headline']
        episode_description = json_data['description']
        podcast_name = json_data['publisher']['name']
        podcast_url = json_data['publisher']['url']
        podcast_author = json_data['author'][0]['name']
        episode_date = json_data['datePublished'][:10]
        podcast_picture = json_data['author'][0]['image']['thumbnailUrl']
        picture_extension = podcast_picture.split('.')[-1]

        if podcast_name and episode_date and episode_title:
            mp3_name = slugify(f'{podcast_name} - {episode_date} - {episode_title}')
        else:
            mp3_name = mp3_url.split('/')[-2]
        if mp3_url and not os.path.exists(os.path.join(output_path, mp3_name + '.mp3')):
            mp3_filename = download_file(output_path, mp3_url, mp3_name + '.mp3')
            art_filename = download_file(output_path, podcast_picture, f'{mp3_name}.{picture_extension}')
            tag_dict = {
                'artist': podcast_author,
                'album': f'Podcast {podcast_name}',
                'title': episode_title,
                'date': episode_date,
                'website': url_parsed.netloc,
                'comment': f'{episode_url}\n{podcast_url}\n{episode_description}',
                'description': f'{episode_url}\n{podcast_url}\n{episode_description}',
                'genre': 'Podcast'
            }
            write_id3_tags_dict(mp3_filename, art_filename, tag_dict)
            return True
    except TimeoutException as ex:
        print(f'Error accessing {episode_url}: Timeout: {str(ex)}')
    except Exception as ex:
        print(f'Error accessing {episode_url}: Exception: {str(ex)}')
    finally:
        driver.close()
    return False
