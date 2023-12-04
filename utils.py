"""
    some utilities
"""
import datetime
import json
import os
import shutil
import zipfile

from slugify import slugify


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
        os.makedirs(dir_path, exist_ok=True)
    dir_path = os.path.join(dir_path, podcast_title)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
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
    with open(os.path.join('res', 'config.json'), 'r') as fp:
        return json.load(fp)
