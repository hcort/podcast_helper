import pytube as pytube
import requests
from mp3_tags import write_id3_tags_dict


def save_image_from_url(thumbnail_url, output_path, nombre):
    import os
    image_path = os.path.join(output_path, f'{nombre}.jpg')
    if not os.path.exists(image_path):
        with open(image_path, 'wb') as handle:
            try:
                response = requests.get(thumbnail_url, stream=True)
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
            'comment': f'{url}\n{yt.channel_url}\n{yt.description}',
            'description': f'{url}\n{yt.channel_url}\n{yt.description}',
            'genre': 'Podcast'
        }
        from slugify import slugify
        nombre = slugify(stream.default_filename[:-4])
        extension = stream.default_filename[-3:]
        stream.download(output_path=output_path, filename=f'{nombre}.{extension}')
        cover_image_filename = save_image_from_url(yt.thumbnail_url, output_path, nombre)
        mp3_filename = mp4_to_mp3(output_path, nombre, extension)
        write_id3_tags_dict(mp3_filename, cover_image_filename, tag_dict)
    except pytube.exceptions.RegexMatchError:
        print("URL no encontrada")
    except BaseException as err:
        print(f"Unexpected {err}, {type(err)}")
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")


def get_youtube_episode(output_path, episode_url):
    youtube_to_mp3(output_path=output_path, url=episode_url)
