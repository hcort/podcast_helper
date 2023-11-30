import os
import moviepy.editor
import pytube
import requests
from slugify import slugify

from mp3_tags import mp4_to_mp3, write_id3_tags_dict


def save_image_from_url(thumbnail_url, output_path, nombre):
    image_path = os.path.join(output_path, f'{nombre}.jpg')
    if not os.path.exists(image_path):
        with open(image_path, 'wb') as handle:
            try:
                response = requests.get(thumbnail_url, stream=True, timeout=30)
                if not response.ok:
                    print('Error getting image: ' + thumbnail_url)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
            except ConnectionError as err:
                print('Error getting image: ' + thumbnail_url)
                print(err)
            except Exception as err:
                print('Error getting image: ' + thumbnail_url)
                print(err)
    return image_path


def youtube_to_mp3(output_path, url):
    try:
        yt = pytube.YouTube(url)
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
        mp3_filename = mp4_to_mp3(output_path, nombre, extension)
        write_id3_tags_dict(mp3_filename=mp3_filename, art_filename=cover_image_filename, tag_dict=tag_dict)
    except pytube.exceptions.RegexMatchError:
        print('URL no encontrada')
    except Exception as err:
        print(f'Unexpected {err}, {type(err)}')
    except BaseException as err:
        print(f'Unexpected {err}, {type(err)}')


def list_videos_from_playlist(playlist_url):
    return [video.watch_url for video in pytube.Playlist(playlist_url).videos]


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
    except BaseException as err:
        print(f'Unexpected {err}, {type(err)}')


def get_youtube_episode(output_path, episode_url):
    youtube_to_mp3(output_path=output_path, url=episode_url)


if __name__ == '__main__':
    # use_proxy = True
    # playlists = [
    #     # Star Wars Galaxy of Creatures
    #     # 'https://www.youtube.com/playlist?list=PLFKE9xs3qYF1T5s5ZSbGsqCwGGK1Wf9A-',
    #     # Star Wars: Galactic Pals
    #     # 'https://www.youtube.com/playlist?list=PLe4ZuWFax2d-t9CPKhlFeY7Y2eVRkfXN3',
    #     # Star Wars. Galaxy of Adventures
    #     'https://www.youtube.com/playlist?list=PLxs2QjD3UrE9xn1ConOtkJM6-inLYEBTT',
    #          ]
    # for playlist in playlists:
    #     all_videos = list_videos_from_playlist(playlist)
    #     for index, link in enumerate(all_videos):
    #         if index == 29:
    #             youtube_download_video('./output', link, index)
    # videos = [
    #     'https://www.youtube.com/watch?v=sDrkc6-_sjo',
    #     'https://www.youtube.com/watch?v=_l8jzFCqryg',
    #     'https://www.youtube.com/watch?v=LURnxaiFE2c'
    # ]
    # for video in videos:
    #     get_youtube_episode('./output', video)
    playlist = 'https://www.youtube.com/playlist?list=PLsQ0j1uzt5dZW12ILjb-8E0s2vw_XJtvj'
    playlist_folder = create_output_folder_playlist(playlist, './output')
    playlist_videos = list_videos_from_playlist(playlist)
    for video in playlist_videos:
        get_youtube_episode(playlist_folder, video)
