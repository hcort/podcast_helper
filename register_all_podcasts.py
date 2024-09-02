"""
    By importing all the files where I have a class that implements AbstractPodcast
    they are registered by the __init_subclass__ call
"""
# pylint: disable=unused-import

from abstract_podcast import AbstractPodcastList
import apple_podcast
import get_substack_audio
import get_youtube_audio
import ivoox
import podbean
import tabs_out_podcast
import upv_video_crawler
import rss_feed_podcast


def create_abstract_podcast_list(output_path):
    return AbstractPodcastList(output_path)
