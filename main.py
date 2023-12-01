"""
    Main entry point

    In main method we can build a list of podcast episodes to download,
    and they will be processed one by one
"""
from register_all_podcasts import create_abstract_podcast_list

output_path_def = r'F:\bkp\podcast'
#
#
# def episode_download(episode_list=None) -> None:
#     if episode_list is not None:
#         for link in episode_list:
#             if link.find('youtube') != -1:
#                 get_youtube_episode(output_path=output_path_def, episode_url=link)
#
#
# def episode_listing():
#     use_proxy = False
#     podcasts = [
#         'https://rereadingwolfe.podbean.com'
#     ]
#     episode_list = []
#     for link in podcasts:
#         if link.find('podbean'):
#             episode_list = get_podbean_episode_list(recycled_driver=None, base_url=link)
#     return episode_list


if __name__ == '__main__':
    # episode_list = episode_listing()
    all_podcasts = create_abstract_podcast_list(output_path_def)
    episode_list = [
        'https://www.ivoox.com/viii-el-enano-blanco-30-los-audios-mp3_rf_111104749_1.html'
    ]
    for episode in episode_list:
        all_podcasts.get_podcast_for_url(episode).get_episode(episode)
    pass
