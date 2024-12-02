"""
    Downloads audio from a youtube video
"""
import os
from urllib.parse import urlparse

import moviepy.editor
import pytube
from slugify import slugify

from abstract_podcast import AbstractPodcast
from mp3_tags import mp4_to_mp3, write_id3_tags_dict
from utils import download_file_requests_stream


class YoutubePodcast(AbstractPodcast):
    """
        Implements AbstractPodcast for youtube
    """

    def __init__(self, output_path=None):
        self.__output_path = output_path

    def check_url(self, url_to_check: str) -> bool:
        return urlparse(url_to_check).hostname.find('youtube') != -1

    def list_episodes(self, start_url: str) -> list:
        return list_videos_from_playlist(start_url)

    def get_episode(self, episode_url: str) -> bool:
        return get_youtube_episode(output_path=self.__output_path, episode_url=episode_url)

    def set_output_path(self, output_path: str):
        self.__output_path = output_path


def save_image_from_url(thumbnail_url, output_path, nombre):
    image_path = os.path.join(output_path, f'{nombre}.jpg')
    if not os.path.exists(image_path):
        download_file_requests_stream(file_url=thumbnail_url, file_name=image_path)
    return image_path


def get_youtube_episode(output_path, episode_url):
    from pytube import YouTube
    from pytube.innertube import _default_clients

    _default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
    _default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID"]
    if not output_path:
        raise FileNotFoundError
    try:
        yt = pytube.YouTube(episode_url)
        stream = yt.streams.filter(mime_type='audio/mp4', only_audio=True).desc().first()
        tag_dict = {
            'artist': yt.author,
            'album': f'Podcast {yt.author}',
            'title': yt.title,
            'date': str(yt.publish_date),
            'length': yt.length,
            'website': yt.channel_url,
            # 'comment': f'{url}\n{yt.channel_url}\n{yt.description}',
            # 'description': f'{url}\n{yt.channel_url}\n{yt.description}',
            'genre': 'Podcast'
        }
        nombre = slugify(stream.default_filename[:-4])
        extension = stream.default_filename[-3:]
        stream.download(output_path=output_path, filename=f'{nombre}.{extension}')
        cover_image_filename = save_image_from_url(yt.thumbnail_url, output_path, nombre)
        mp3_filename = mp4_to_mp3(output_path, nombre, extension, delete_mp4=True)
        write_id3_tags_dict(mp3_filename, cover_image_filename, tag_dict)
        return True
    except pytube.exceptions.RegexMatchError as e:
        print(f'URL no encontrada - {e}')
    except Exception as err:
        print(f'Unexpected {err}, {type(err)}')
    except BaseException as err:
        print(f'Unexpected {err}, {type(err)}')
    return False


def list_videos_from_playlist(playlist_url):
    all_videos = pytube.Playlist(playlist_url).videos
    return [video.watch_url for video in all_videos]


def create_output_folder_playlist(playlist_url, output_root):
    pl = pytube.Playlist(playlist_url)
    normalized_name = slugify(f'{pl.owner}-{pl.title}')
    full_path = os.path.join(output_root, normalized_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path


def youtube_download_video(output_path, url, index=0):
    try:
        yt = pytube.YouTube(url)
        video_stream = yt.streams.filter(mime_type='video/mp4', res='1080p').desc().first()
        video_stream.download(
            output_path=output_path, filename='temp_video.mp4')

        # Download audio and rename
        # audio_stream = pytube.YouTube(url).streams.filter(only_audio=True).desc().first().download(
        #     output_path=output_path, filename='temp_audio.mp4'
        # )

        # Setting the audio to the video
        temp_yt_video = moviepy.editor.VideoFileClip(os.path.join(output_path, 'temp_video.mp4'))
        temp_yt_audio = moviepy.editor.AudioFileClip(os.path.join(output_path, 'temp_audio.mp4'))
        final = temp_yt_video.set_audio(temp_yt_audio)

        # Output result

        # Delete video and audio to keep the result
        nombre = slugify(video_stream.default_filename[:-4])
        extension = video_stream.default_filename[-3:]
        final_filename = os.path.join(output_path, f'{index} - {nombre}.{extension}')
        final.write_videofile(final_filename)

        os.remove(os.path.join(output_path, 'temp_video.mp4'))
        os.remove(os.path.join(output_path, 'temp_audio.mp4'))
    except pytube.exceptions.RegexMatchError:
        print('URL no encontrada')
    except Exception as err:
        print(f'Unexpected {err}, {type(err)}')

