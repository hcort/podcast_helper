"""
    Main entry point

    In main method we can build a list of podcast episodes to download,
    and they will be processed one by one
"""
from get_driver import close_and_remove_driver
from register_all_podcasts import create_abstract_podcast_list

output_path_def = r'F:\bkp\podcast'


if __name__ == '__main__':
    all_podcasts = create_abstract_podcast_list(output_path_def)
    episode_list = []
    for episode in episode_list:
        all_podcasts.get_podcast_for_url(episode).get_episode(episode)
    close_and_remove_driver()
