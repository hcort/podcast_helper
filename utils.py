"""
    some utilities
"""
import os
import datetime

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
