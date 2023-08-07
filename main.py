from get_episode import get_ivoox_episode
from get_substack_audio import get_substack_episode
from get_youtube_audio import get_youtube_episode

output_path_def = './output'


if __name__ == '__main__':
    links = [
             ]
    for link in links:
        if link.find('youtube') != -1:
            get_youtube_episode(output_path=output_path_def, episode_url=link)
        elif link.find('ivoox') != -1:
            get_ivoox_episode(output_path=output_path_def, episode_url=link)
        elif link.find('substack') != -1:
            get_substack_episode(output_path=output_path_def, episode_url=link)
