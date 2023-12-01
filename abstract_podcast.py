"""
    Abstract representation of a podcast wrapper

    All podcast downloaders must implement this interface
"""


class AbstractPodcast:
    subclasses = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    def check_url(self, url_to_check: str) -> bool:
        raise NotImplementedError

    def list_episodes(self, start_url: str) -> list:
        raise NotImplementedError

    def get_episode(self, episode_url: str) -> bool:
        raise NotImplementedError

    def set_output_path(self, output_path: str):
        raise NotImplementedError


class AbstractPodcastList:

    def __init__(self, output_path):
        self.__registered_podcasts = []
        for podcast_class in AbstractPodcast.subclasses:
            new_podcast = podcast_class()
            new_podcast.set_output_path(output_path)
            self.__registered_podcasts.append(new_podcast)

    def get_podcast_for_url(self, podcast_url):
        for p in self.__registered_podcasts:
            if p.check_url(podcast_url):
                return p
        return None
