"""
    Gets episodes from the podcast

    Using the Firefox driver we click the button that goes to the mp3 file and stop the navigation.
    With the URL of the webdriver we create a Requests object to download the mp3 file.

    Using the Opera driver we have to inject some Javascript to do the download. Then we wait for the file
    and put it in the output folder

"""
import os
import re
import time
from time import sleep
from urllib.parse import urlparse

import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from slugify import slugify

from abstract_podcast import AbstractPodcast
from get_driver import get_driver
from get_driver import hijack_cookies, get_driver_opera
from mp3_tags import write_mp3_tags
from utils import create_filename_and_folders, file_exists, get_file_requests


rgx_episode_id = re.compile('_rf_([0-9]+)_([0-9])')


class IvooxPodcast(AbstractPodcast):
    """
        implements AbstractPodcast for ivoox
    """

    def __init__(self, output_path=None):
        self.__output_path = output_path

    def check_url(self, url_to_check: str) -> bool:
        return urlparse(url_to_check).hostname.find('ivoox') != -1

    def list_episodes(self, start_url: str) -> list:
        return list_episodes_simple(start_url)

    def get_episode(self, episode_url: str) -> bool:
        return get_episode(output_path=self.__output_path, episode_url=episode_url)

    def set_output_path(self, output_path: str):
        self.__output_path = output_path


def wait_for_cookies(webdriver_waiting_for_cookies, timeout, url):
    if webdriver_waiting_for_cookies.get_cookie('cookies_policy_accepted'):
        return
    try:
        cookie_button_present = EC.presence_of_element_located((By.ID, 'didomi-notice-agree-button'))
        WebDriverWait(webdriver_waiting_for_cookies, timeout).until(cookie_button_present)
        cookie_button = webdriver_waiting_for_cookies.find_element(By.ID, 'didomi-notice-agree-button')
        cookie_button.click()
        WebDriverWait(webdriver_waiting_for_cookies, timeout).until_not(cookie_button_present)
    except TimeoutException as ex:
        # cookies already accepted
        print(f'Error clicking cookies button {url} - {ex}')


def initialize_episode_list(prev_page, page_no):
    return {
        'prev_page': prev_page,
        'page_no': page_no,
        'episode_list': [],
        'next_page': ''
    }


def list_episodes_simple(start_url):
    episode_list = []
    next_page = start_url
    while next_page:
        episodes_in_page = list_episodes(next_page)
        episode_list.extend([x['url'] for x in episodes_in_page['episode_list']])
        next_page = '' if episodes_in_page['next_page'].find(next_page) >= 0 else episodes_in_page['next_page']
    return episode_list


def list_episodes(start_url=None, prev_page='', page_no=1):
    webdriver = get_driver()
    if (not webdriver) or (not start_url):
        return None
    # if not base_url or not current_url or not webdriver:
    if not start_url:
        return None
    episodes_in_page = initialize_episode_list(prev_page, page_no)
    timeout = 5
    webdriver.get(start_url)
    wait_for_cookies(webdriver, timeout, start_url)
    try:
        next_page_present = EC.presence_of_element_located(
            (By.CLASS_NAME, 'title-wrapper'))
        WebDriverWait(webdriver, timeout).until(next_page_present)
        all_titles_p = webdriver.find_elements(By.CLASS_NAME, 'title-wrapper')
        all_description_buttons = webdriver.find_elements(By.CLASS_NAME, 'btn.btn-link.info')
        all_short_descriptions = webdriver.find_elements(By.CLASS_NAME, 'audio-description')
        for _, (title, button, short_description) in enumerate(zip(
                all_titles_p,
                all_description_buttons,
                all_short_descriptions)):
            link_element = title.find_element(By.TAG_NAME, 'a')
            if not link_element:
                continue
            link = title.find_element(By.TAG_NAME, 'a').get_attribute('href')
            description = short_description.text
            try:
                webdriver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0,-200)", button)
                time.sleep(1)
                button.click()
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'popover-content'))
                WebDriverWait(webdriver, timeout).until(element_present)
                description = webdriver.find_element(By.CLASS_NAME, 'popover-content').text
                # button.click()
                webdriver.find_element(By.TAG_NAME, 'body').click()
                WebDriverWait(webdriver, timeout).until_not(element_present)
            except Exception as err:
                print(f'Error clicking description: {err}')
            episodes_in_page['episode_list'].append({'url': link, 'desc': description})
        next_page_button = webdriver.find_elements(By.CSS_SELECTOR, 'ul.pagination > li > a')
        episodes_in_page['next_page'] = next_page_button[-1].get_attribute('href') if next_page_button else ''
    except TimeoutException as ex:
        print(f'Error accessing {webdriver.current_url}: Timeout: {str(ex)}')
    except Exception as ex:
        print(f'Error accessing {webdriver.current_url}: Unknown error: {str(ex)}')
    return episodes_in_page


def set_headers(requests_session, referer_url):
    headers = {
            'authority': 'www.ivoox.com',
            'accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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


def get_episode_cover_art(webdriver, output_dir, podcast_title):
    img_tag = webdriver.find_element(By.CSS_SELECTOR, 'div.layout-2-colums div.d-flex div.image-wrapper img')
    img_url = img_tag.get_attribute('src')
    img_req = requests.get(img_url, timeout=50)
    img_filename = create_filename_and_folders(output_dir, podcast_title, img_url)
    ext_sep = img_filename.rfind('-', len(img_filename) - 5, len(img_filename))
    img_filename = img_filename[:ext_sep - 1] + '.' + img_filename[ext_sep + 1:]
    with open(img_filename, mode='wb') as localfile:
        localfile.write(img_req.content)
    return img_filename


def remove_promo_popup(driver):
    timeout = 5
    try:
        promo_layer = EC.presence_of_element_located((By.ID, 'promo-starter'))
        WebDriverWait(driver, timeout).until(promo_layer)
        promo_layer = driver.find_element(By.ID, 'promo-starter')
        driver.execute_script("""var element = arguments[0];
                    element.innerHTML = '';""", promo_layer)
        promo_layer.click()
        time.sleep(5)
    except TimeoutException:
        pass


def get_episode(output_path, episode_url):
    driver = get_driver()
    timeout = 5
    if not episode_url or not driver:
        return None
    driver.get(episode_url)
    wait_for_cookies(driver, timeout=10, url=episode_url)
    try:
        remove_promo_popup(driver)

        try:
            if driver.find_element(By.ID, 'apoyar-btn'):
                print(f'The episode {episode_url} is behind the paywall - Can\'t download')
                return False
        except Exception:
            # if the element is not present then we are in a regular episode
            pass

        podcast_title = driver.find_elements(By.CSS_SELECTOR, 'div.mb-6 > div.mb-2 > a')[1].text
        podcast_date = driver.find_element(By.CSS_SELECTOR, 'div.play-features-1 > div > span').text.split('·')[0].strip()
        episode_title = driver.find_element(By.CLASS_NAME, 'h2').text

        btn_dnl = driver.find_element(By.CSS_SELECTOR, 'div.play-features-1 div.stat  button')
        btn_dnl.click()
        time.sleep(1)

        div_pop_up = btn_dnl.find_element(By.XPATH, './preceding-sibling::div')
        div_pop_up_links = div_pop_up.find_elements(By.TAG_NAME, 'a')
        div_pop_up_links[2].click()

        import re
        # m = re.compile('_rf_([0-9]+)_([0-9])').search(episode_url)
        rgx_match = rgx_episode_id.search(episode_url)
        if rgx_match:
            episode_id = rgx_match.group(1)
            # get download url from JSON
            requests_session = hijack_cookies(driver)
            requests_session = set_headers(requests_session, episode_url)
            download_url_json = requests_session.get(f'https://vcore-web.ivoox.com/v1/public/audios/{episode_id}/download-url')
            download_url = download_url_json.json()['data']['downloadUrl']
            redirect_url = f'https://www.ivoox.com{download_url}'
            mp3_filename = create_filename_and_folders(output_path, podcast_title, episode_title) + '.mp3'
            get_file_requests(requests_session, redirect_url, mp3_filename)
            image_filename = get_episode_cover_art(driver, output_path, slugify(podcast_title))
            write_mp3_tags(episode_title, podcast_title, podcast_date, image_filename, mp3_filename)
            return True
    except TimeoutException as ex:
        # cookies already accepted
        print(f'Could not download episode {episode_url} - {ex}')
    except Exception as ex:
        print(f'Could not download episode {episode_url} - {ex}')
    return False


def expand_download_button(driver, timeout):
    download_buttons_present = EC.presence_of_element_located((By.ID, 'lnk_download'))
    WebDriverWait(driver, timeout).until(download_buttons_present)
    download_buttons = driver.find_elements(By.ID, 'lnk_download')
    download_buttons[1].click()
    next_page_present = EC.presence_of_element_located((By.CLASS_NAME, 'downloadlink'))
    WebDriverWait(driver, timeout).until(next_page_present)
    download_links_container = driver.find_element(By.CLASS_NAME, 'downloadlink')
    download_links = download_links_container.find_elements(By.TAG_NAME, 'a')
    return download_links[0]


def get_episode_opera_vpn(episode=None, output_dir=None):
    """

    :param driver:
    :param episode:
    :param output_dir:
    :return:

        Download a podcast episode using the Opera webdriver with the VPN enabled to avoid firewall blocks

        I can't use the requests method to download the episode, as it's outside the Opera VPN, so I use
        injected javascript to download the file into Opera's download folder and then move it to
        the output_dir folder

    """
    timeout = 5
    driver = get_driver_opera()
    if not episode or not driver:
        return None
    driver.get(episode)
    wait_for_cookies(driver, timeout=10, url=episode)
    try:
        podcast_title = driver.find_element(By.CLASS_NAME, 'normal').get_attribute('title')
        podcast_date = driver.find_element(By.CLASS_NAME, 'icon-date').text
        episode_title = driver.find_element(By.TAG_NAME, 'h1').text
        mp3_filename = create_filename_and_folders(output_dir, podcast_title, episode_title) + '.mp3'
        download_link = expand_download_button(driver, timeout)
        download_link.click()
        audio_source_present = EC.presence_of_element_located((By.TAG_NAME, 'source'))
        WebDriverWait(driver, timeout).until(audio_source_present)
        mp3_link = driver.find_element(By.TAG_NAME, 'source').get_attribute('src')
        parsed_url = urlparse(mp3_link)
        mp3_filename_from_url = parsed_url.path[parsed_url.path.rfind('/')+1:]
        temp_mp3_full_path = os.path.join(output_dir, mp3_filename_from_url)
        driver.execute_script('let aLink = document.createElement("a");'
                              'let videoSrc = document.querySelector("video").firstChild.src;'
                              'aLink.href = videoSrc;'
                              'aLink.download = "";'
                              'aLink.click();')
        # wait for download t complete
        while not os.path.isfile(temp_mp3_full_path):
            sleep(3)
        os.replace(temp_mp3_full_path, mp3_filename)
        write_mp3_tags(entry_title=episode_title, podcast_title=podcast_title, entry_date=podcast_date,
                       art_filename=None, mp3_name=mp3_filename)
    except TimeoutException as ex:
        # cookies already accepted
        print(f'Could not download episode {episode} - {ex}')
    except Exception as ex:
        print(f'Could not download episode {episode} - {ex}')
