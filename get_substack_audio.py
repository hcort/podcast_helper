import os
import time
from urllib.parse import urlparse
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from import_selenium_cond import Keys
from selenium.webdriver.common.by import By
from slugify import slugify
from tqdm import tqdm
import json

from mp3_tags import write_id3_tags_dict


class ProgressVisorTQDM:
    def __init__(self, message: str):
        self.total_iterations = 0
        self.__tqdm_progress = tqdm(position=0, leave=True, desc=message)

    @property
    def total(self):
        return self.total_iterations

    @total.setter
    def total(self, total_iterations):
        self.total_iterations = total_iterations
        self.__tqdm_progress.total = total_iterations

    def update(self):
        self.__tqdm_progress.update()


def download_file(output_path, link, name, show_progress=False):
    filename = os.path.join(output_path, name)
    if not os.path.exists(filename):
        with open(filename, 'wb') as handle:
            try:
                response = requests.get(link, stream=True, timeout=100)
                block_size = 1024 * 64
                progress = None
                if show_progress:
                    progress = ProgressVisorTQDM(f'Downloading\n{link} -> {filename}\n')
                    progress.total = int(response.headers.get('content-length')) // block_size
                if not response.ok:
                    print('Error getting file: ' + link)
                for block in response.iter_content(block_size):
                    if not block:
                        break
                    handle.write(block)
                    if progress:
                        progress.update()
            except ConnectionError as err:
                print('Error getting file: ' + link)
                print(err)
            except Exception as err:
                print('Error getting file: ' + link)
                print(err)
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
        elements = driver.find_elements(By.TAG_NAME, "audio")
        mp3_url = elements[0].get_attribute("src") if (len(elements) > 0) else ''
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
    except TimeoutException as ex:
        print(f'Error accessing {episode_url}: Timeout: {str(ex)}')
    except Exception as ex:
        print(f'Error accessing {episode_url}: Exception: {str(ex)}')
    finally:
        driver.close()
