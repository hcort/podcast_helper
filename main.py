"""
    Main entry point

    In main method we can build a list of podcast episodes to download,
    and they will be processed one by one
"""
from apple_podcast import get_apple_podcast_episode
from episode_list import get_ivoox_episode_list
from get_episode import get_ivoox_episode
from get_substack_audio import get_substack_episode
from get_youtube_audio import get_youtube_episode
from podbean import get_podbean_episode, get_podbean_episode_list

output_path_def = './output'


def episode_download(episode_list=None) -> None:
    if episode_list is not None:
        use_proxy = False
        for link in episode_list:
            if link.find('youtube') != -1:
                get_youtube_episode(output_path=output_path_def, episode_url=link)
            elif link.find('ivoox') != -1:
                get_ivoox_episode(output_path=output_path_def, episode_url=link, use_web_proxy=use_proxy)
            elif link.find('substack') != -1:
                get_substack_episode(output_path=output_path_def, episode_url=link)
            elif link.find('podbean') != -1:
                get_podbean_episode(output_path=output_path_def, episode_url=link)
            elif link.find('apple.com') != -1:
                get_apple_podcast_episode(output_path=output_path_def, episode_url=link)


def episode_listing():
    use_proxy = False
    podcasts = [
        'https://rereadingwolfe.podbean.com'
    ]
    episode_list = []
    for link in podcasts:
        # if link.find('youtube') != -1:
        #     get_youtube_episode(output_path=output_path_def, episode_url=link)
        if link.find('ivoox') != -1:
            episode_list = get_ivoox_episode_list(recycled_driver=None, podcast_url=link, use_web_proxy=use_proxy)
        # elif link.find('substack') != -1:
        #     get_substack_episode(output_path=output_path_def, episode_url=link)
        elif link.find('podbean'):
            episode_list = get_podbean_episode_list(recycled_driver=None, base_url=link)
    return episode_list


if __name__ == '__main__':
    # episode_list = episode_listing()
    episode_download()
