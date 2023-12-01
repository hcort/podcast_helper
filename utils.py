"""
    some utilities
"""
import json
import os

from slugify import slugify


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
    with os.open(os.join('res', 'config.json'), 'r') as fp:
        return json.load(fp)
