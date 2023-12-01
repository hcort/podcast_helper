"""
    Abstract representation of a podcast wrapper

    All podcast downloaders must implement this interface
"""


class AbstractPodcast:

    def check_url(self, url_to_check: str) -> bool:
        raise NotImplementedError

    def list_episodes(self, start_url: str) -> list:
        raise NotImplementedError

    def get_episode(self, episode_url: str) -> bool:
        raise NotImplementedError


class AbstractPodcastList:

    def __init__(self):
        self.__registered_podcasts = []

    def register_podcast(self, new_podcast: AbstractPodcast):
        self.__registered_podcasts.append(new_podcast)

    def get_podcast_for_url(self, podcast_url):
        for p in self.__registered_podcasts:
            if p.check_url(podcast_url):
                return p
        return None

all_registered_podcasts = AbstractPodcastList
