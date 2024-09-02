"""
    some utilities
"""
import os
import datetime
import shutil

import requests
from bs4 import BeautifulSoup
from slugify import slugify


def get_file_requests(requests_session, url, filename):
    if file_exists(filename):
        return True
    response = requests_session.get(url)
    with open(filename, mode='wb') as localfile:
        localfile.write(response.content)


def file_exists(filename):
    if os.path.exists(filename):
        st = os.stat(filename)
        # file bigger than 5 MB
        if (st.st_size >> 20) > 5:
            mod_time = datetime.date.fromtimestamp(st.st_mtime)
            delta = datetime.datetime.today().date() - mod_time
            if delta.days > 1:
                return True
    return False


def download_file_requests_stream(file_url, file_name, block_size=1):
    with open(file_name, 'wb') as handle:
        try:
            response = requests.get(file_url, stream=True, timeout=30)
            if not response.ok:
                print(f'Error getting file: {file_url} - HTTP error')
            for block in response.iter_content(1024*block_size):
                if not block:
                    break
                handle.write(block)
        except ConnectionError as err:
            print(f'Error getting file: {file_url} - {err}')
        except Exception as err:
            print(f'Error getting file: {file_url} - {err}')


def get_soup_from_requests(podcast_url):
    response = requests.get(podcast_url,
                            headers={'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'},
                            timeout=10)
    if not response.ok:
        print(f'Error getting page: {podcast_url}')
        return None
    return BeautifulSoup(response.text, features='html.parser')


def zip_folder(base_folder, folder):
    origin_folder = os.path.join(base_folder, folder)
    filename = f'{folder}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
    fullname = os.path.join(base_folder, filename)
    shutil.make_archive(fullname, 'zip', origin_folder)
    return f'{filename}.zip'


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


def read_config_object():
    """
        Config object:
        {
          "output_folder": "...",
          "firefox_location":
          {
            "windows": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "linux": ""
          }
        }
    :return:
    """
    with open(os.path.join('res', 'config.json'), 'r', encoding='utf-8') as fp:
        return json.load(fp)
