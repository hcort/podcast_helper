"""
    Podbean has a website that can be crawled and a RSS feed with direct links to each epidose
"""
import json
import time

import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from get_driver import get_driver, hijack_cookies
from get_episode import create_filename_and_folders
from mp3_tags import write_mp3_tags


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


def get_episode(driver, episode, output_dir):
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


def get_episode_list(driver, podcast):
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


def get_podbean_episode(output_path, episode_url, recycled_driver=None):
    driver = recycled_driver if recycled_driver else get_driver()
    get_episode(driver=driver, episode=episode_url, output_dir=output_path)
    if not recycled_driver:
        driver.close()


def get_podbean_episode_list(base_url, recycled_driver=None):
    driver = recycled_driver if recycled_driver else get_driver()
    episode_list = get_episode_list(driver=driver, podcast=base_url)
    if not recycled_driver:
        driver.close()
    return episode_list
