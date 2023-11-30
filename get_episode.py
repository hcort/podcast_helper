"""
    Gets episodes from the podcast

    Using the Firefox driver we click the button that goes to the mp3 file and stop the navigation.
    With the URL of the webdriver we create a Requests object to download the mp3 file.

    Using the Opera driver we have to inject some Javascript to do the download. Then we wait for the file
    and put it in the output folder

"""
import os
from time import sleep
import requests
# from selenium.common import TimeoutException
# from selenium.webdriver import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from slugify import slugify
from urllib.parse import urlparse

from episode_list import wait_for_cookies
from get_driver import hijack_cookies, get_driver
from mp3_tags import write_mp3_tags


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


def create_filename_and_folders(output_dir, podcast_title, filename):
    if not output_dir:
        output_dir = 'temp_output_dir'
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), output_dir)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    dir_path = os.path.join(dir_path, podcast_title)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return os.path.join(dir_path, slugify(filename, max_length=200))


def get_episode_cover_art(webdriver, output_dir, podcast_title):
    img_tag = webdriver.find_element(By.CLASS_NAME, 'main.lozad.elevate-2')
    img_url = img_tag.get_attribute('src')
    img_req = requests.get(img_url, timeout=50)
    img_filename = create_filename_and_folders(output_dir, podcast_title, img_url)
    ext_sep = img_filename.rfind('-', len(img_filename) - 5, len(img_filename))
    img_filename = img_filename[:ext_sep - 1] + '.' + img_filename[ext_sep + 1:]
    with open(img_filename, mode='wb') as localfile:
        localfile.write(img_req.content)
    return img_filename


def get_episode(driver=None, episode='', output_dir='', use_web_proxy=False):
    timeout = 5
    if not episode or not driver:
        return None
    if use_web_proxy:
        proxy_server_option = 'eu15'
        driver.get(f'https://{proxy_server_option}.proxysite.com')
        proxy_input = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[1]/div/div[3]/form/div[2]/input')
        proxy_input.send_keys(episode)
        proxy_input.send_keys(Keys.RETURN)
    else:
        driver.get(episode)
    wait_for_cookies(driver, timeout=10, url=episode)
    try:
        podcast_title = driver.find_element(By.CLASS_NAME, 'normal').get_attribute('title')
        podcast_date = driver.find_element(By.CLASS_NAME, 'icon-date').text
        episode_title = driver.find_element(By.TAG_NAME, 'h1').text
        download_link = expand_download_button(driver, timeout)
        requests_session = hijack_cookies(driver)
        requests_session = set_headers(requests_session, download_link.get_attribute('href'))
        mp3_link = download_link.get_attribute('href')
        redirected = requests_session.get(mp3_link)
        mp3_filename_end = redirected.url.find('.mp3')
        mp3_filename_start = redirected.url.rfind('/', 0, mp3_filename_end)
        mp3_filename = redirected.url[mp3_filename_start+1:mp3_filename_end+4]
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


def get_episode_opera_vpn(driver=None, episode=None, output_dir=None):
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


def get_all_episodes(driver=None, episode_list=None):
    if not episode_list or not driver:
        return None
    for episode in episode_list:
        get_episode(driver, episode)


def get_ivoox_episode(output_path, episode_url, recycled_driver=None, use_web_proxy=False):
    driver = recycled_driver if recycled_driver else get_driver()
    get_episode(driver=driver, episode=episode_url, output_dir=output_path, use_web_proxy=use_web_proxy)
    if not recycled_driver:
        driver.close()


def get_ivoox_episode_opera(output_path, episode_url, recycled_driver=None):
    driver = recycled_driver if recycled_driver else get_driver()
    get_episode_opera_vpn(driver=driver, episode=episode_url, output_dir=output_path)
    if not recycled_driver:
        driver.close()
