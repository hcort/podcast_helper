"""
    RSS feed based podcast

    Special case, as the XML already contains the mp3 urls, so I can download
    the episodes while I list them
"""
import os.path

import feedparser
from slugify import slugify

from abstract_podcast import AbstractPodcast
from mp3_tags import write_mp3_tags
from utils import download_file_requests_stream, create_filename_and_folders, get_soup_from_requests


class RssFeedPodcast(AbstractPodcast):
    """
        implements AbstractPodcast for ivoox
    """

    def __init__(self, output_path=None):
        self.__output_path = output_path
        self.__download_during_list = True

    def check_url(self, url_to_check: str) -> bool:
        return False

    def list_episodes(self, start_url: str) -> list:
        return self._list_episodes_simple(start_url)

    def get_episode(self, episode_url: str) -> bool:
        return self._get_episode(episode_url=episode_url)

    def set_output_path(self, output_path: str):
        self.__output_path = output_path

    def disable_download_during_list(self):
        self.__download_during_list = False

    def _list_episodes_simple(self, start_url):
        all_episodes = []
        feed = feedparser.parse(start_url)
        for item in feed.entries:
            all_episodes.append(item['link'])
            if self.__download_during_list:
                self._parse_feed_item(item, feed)
        return all_episodes

    def _get_episode(self, episode_url):
        soup = get_soup_from_requests(episode_url)
        if not soup:
            return
        rss_url = soup.select_one('nav.link-list-inline-row ul li a.btn')['href']
        feed = feedparser.parse(rss_url)
        for item in feed.entries:
            if item['link'] == episode_url:
                self._parse_feed_item(item, feed)
                return True
        return False

    def _parse_feed_item(self, item, feed):
        episode_title = item['title']
        podcast_title = feed['feed']['title']
        podcast_date = item['published']
        podcast_mp3_url = item['links'][1]['href']
        mp3_filename = create_filename_and_folders(self.__output_path, slugify(podcast_title), episode_title) + '.mp3'
        if os.path.isfile(mp3_filename):
            return
        download_file_requests_stream(podcast_mp3_url, mp3_filename)
        write_mp3_tags(episode_title, podcast_title, podcast_date, None, mp3_filename)


class WeirdStudiesPodcast(RssFeedPodcast):
    """
        implements AbstractPodcast for Weird Studies
    """

    def check_url(self, url_to_check: str) -> bool:
        return url_to_check.find('weirdstudies') != -1
