"""
    Methods to handle the mp3 ID3 tags
"""
import os
import moviepy.editor as mp
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3


def check_file_type(file_path):
    try:
        audio = File(file_path)
        if audio is None:
            print(f"The file {file_path} is not a supported audio/video format.")
        else:
            format_type = audio.__class__.__name__
            return format_type
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return None


def mp4_to_mp3(path, mp4_name, extension='mp4', delete_mp4=False):
    mp4_file = os.path.join(path, f'{mp4_name}.{extension}')
    mp3_file = os.path.join(path, f'{mp4_name}.mp3')
    if not os.path.exists(mp3_file):
        clip = mp.AudioFileClip(mp4_file)
        clip.write_audiofile(mp3_file)
    if delete_mp4:
        os.remove(mp4_file)
    return mp3_file


def write_cover_art(art_filename, mp3_name):
    if not art_filename:
        return
    print(f'writing {art_filename} into {mp3_name}')
    try:
        audio = MP3(mp3_name)
        audio.add_tags()
    except Exception:
        pass
    try:
        audio = MP3(mp3_name)
        mime = 'image/png' if art_filename.endswith('png') else 'image/jpeg'
        file = open(art_filename, 'rb')
        data = file.read()
        audio.tags.add(
            APIC(
                encoding=3,  # 3 is for utf-8
                mime=mime,  # image/jpeg or image/png
                type=3,  # 3 is for the cover image
                desc='Cover',
                data=data
            )
        )
        audio.save()
    except Exception as ex:
        print(f'Can\'t save cover image: {ex}')


# writes some basic ID3 tags to the mp3 file
def write_mp3_tags(entry_title, podcast_title, entry_date, art_filename, mp3_name):
    write_cover_art(art_filename, mp3_name)
    # audio = EasyID3(mp3_name)
    try:
        audio = EasyID3(mp3_name)
    except ValueError:
        audio = File(mp3_name, easy=True)
        audio.add_tags()
    audio['title'] = entry_title
    audio['artist'] = podcast_title
    audio['album'] = f'Podcast {podcast_title}'
    audio['date'] = entry_date
    audio['genre'] = 'Podcast'
    audio.save()


def write_id3_tags_dict(mp3_filename, art_filename, tag_dict=None):
    if tag_dict is None:
        tag_dict = {}
    try:
        meta = EasyID3(mp3_filename)
    except ValueError:
        meta = File(mp3_filename, easy=True)
        meta.add_tags()
    for tag in tag_dict:
        try:
            meta[tag] = tag_dict[tag]
        except ValueError as err:
            # mp3 and mp4 files have different sets of valid tags
            print(err)
    meta.save()
    if art_filename:
        write_cover_art(mp3_filename, art_filename)
