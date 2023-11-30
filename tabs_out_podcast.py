"""
    Tabs out is a podcast hosted in a custom website


    post-pagination
"""
from typing import List, Any

import requests
from bs4 import BeautifulSoup
from slugify import slugify

from get_episode import create_filename_and_folders
from main import output_path_def
from mp3_tags import write_mp3_tags


def get_tabs_out_episode_list():
    podcast_url = 'https://tabsout.com/?cat=5'
    episodes = []
    try:
        while True:
            response = requests.get(podcast_url, headers={"Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"})
            if not response.ok:
                print(f'Error getting index: {podcast_url}')
                break
            soup = BeautifulSoup(response.text, features="html.parser")
            links = soup.select('a.ek-link')
            episodes.extend([l.get('href', '') for l in links])
            next_page = soup.select_one('a.next')
            podcast_url = next_page.get('href', '') if next_page else ''
    except Exception as err:
        print(f'Error getting episode list: {podcast_url} - {err}')
    return episodes


def get_episode_cover_art(output_dir, podcast_title, img_url):
    img_req = requests.get(img_url)
    img_filename = create_filename_and_folders(output_dir, podcast_title, img_url)
    ext_sep = img_filename.rfind('-', len(img_filename) - 5, len(img_filename))
    img_filename = img_filename[:ext_sep - 1] + '.' + img_filename[ext_sep + 1:]
    with open(img_filename, mode='wb') as localfile:
        localfile.write(img_req.content)
    return img_filename


def get_episode(episode_url):
    """
    <audio playsinline="" preload="auto" class="player29594" id="player29594">
      <source src="https://tabsout.com/episodes/193.mp3" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    :param episode_url:
    :return:
    """
    response = requests.get(episode_url, headers={"Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"})
    if not response.ok:
        print(f'Error getting index: {episode_url}')
        return
    soup = BeautifulSoup(response.text, features="html.parser")
    episode_title = soup.select_one('h2.wp-block-heading').text
    episode_author = 'Tabs Out'
    episode_album = 'Podcast Tabs Out'
    podcast_date = soup.select_one('div.entry-content-inner > p').text
    podcast_artwork = soup.select_one('a.flexia-header-logo > img').get('src', '')

    audio = soup.select_one('audio > source')
    if not audio:
        audio = soup.select_one('audio')
    mp3_link = soup.select_one('audio > source').get('src', None)
    if mp3_link:
        redirected = requests.get(mp3_link)
        mp3_filename = create_filename_and_folders(output_dir=output_path_def,
                                                   podcast_title=slugify(episode_album),
                                                   filename=episode_title) + '.mp3'
        with open(mp3_filename, mode='wb') as localfile:
            localfile.write(redirected.content)
        image_filename = get_episode_cover_art(output_dir=output_path_def,
                                               podcast_title=slugify(episode_album),
                                               img_url=podcast_artwork)
        write_mp3_tags(episode_title, episode_author, podcast_date, image_filename, mp3_filename)


if __name__ == '__main__':
    episode_list = get_tabs_out_episode_list()
    for episode in episode_list:
        get_episode(episode)
