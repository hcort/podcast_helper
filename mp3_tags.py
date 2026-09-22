"""
    Methods to handle the mp3 ID3 tags
"""
import os
import moviepy.editor as mp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, COMM, ID3, ID3NoHeaderError, TXXX, USLT, WOAR, WOAS
from mutagen.mp3 import MP3
from mutagen import File


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
    art_filename = os.fspath(art_filename)
    mp3_name = os.fspath(mp3_name)
    print(f'writing {art_filename} into {mp3_name}')
    try:
        audio = MP3(mp3_name)
        audio.add_tags()
    except Exception:
        pass
    try:
        audio = MP3(mp3_name)
        mime = 'image/png' if art_filename.lower().endswith('.png') else 'image/jpeg'
        with open(art_filename, 'rb') as file:
            data = file.read()
        audio.tags.delall('APIC:Cover')
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


def _tag_values(value):
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if item is not None]
    return [] if value is None else [str(value)]


def _write_id3_values(mp3_name, tag_dict):
    """Write standard ID3 fields and preserve arbitrary fields as TXXX frames."""
    try:
        easy_tags = EasyID3(mp3_name)
    except ID3NoHeaderError:
        easy_tags = EasyID3()

    raw_tags = {}
    for original_key, value in tag_dict.items():
        if value is None:
            continue
        key = str(original_key).lower().replace('-', '_').replace(' ', '_')
        values = _tag_values(value)
        if not values:
            continue
        try:
            easy_tags[key] = values
        except (KeyError, ValueError):
            raw_tags[key] = values
    easy_tags.save(mp3_name)

    tags = ID3(mp3_name)
    source_url_keys = {'source_url', 'webpage_url', 'purl', 'url'}
    artist_url_keys = {'artist_url', 'channel_url'}
    comment_keys = {'comment', 'description', 'synopsis'}
    lyric_keys = {'lyrics', 'unsyncedlyrics'}
    descriptions = {
        'youtube_id': 'YouTube ID',
        'channel_id': 'YouTube Channel ID',
        'uploader_id': 'YouTube Uploader ID',
        'youtube_categories': 'YouTube Categories',
        'youtube_tags': 'YouTube Tags',
    }
    for key, values in raw_tags.items():
        description = descriptions.get(key, key.replace('_', ' ').title())
        if key in source_url_keys:
            tags.delall('WOAS')
            tags.add(WOAS(url=values[0]))
        elif key in artist_url_keys:
            tags.delall('WOAR')
            tags.add(WOAR(url=values[0]))
        elif key in comment_keys:
            tags.delall(f'COMM:{description}:eng')
            tags.add(COMM(encoding=3, lang='eng', desc=description, text=values))
        elif key in lyric_keys:
            tags.delall(f'USLT:{description}:eng')
            tags.add(USLT(encoding=3, lang='eng', desc=description, text='\n'.join(values)))
        else:
            tags.delall(f'TXXX:{description}')
            tags.add(TXXX(encoding=3, desc=description, text=values))
    tags.save(v2_version=3)


def write_mp3_tags(entry_title, podcast_title, entry_date, art_filename, mp3_name, tag_dict=None):
    """Write podcast ID3 tags, optionally extended or overridden by tag_dict.

    EasyID3-compatible keys are written as standard frames. URLs, comments,
    descriptions and lyrics use their dedicated ID3 frames; any other key is
    retained as a user-defined TXXX frame.
    """
    values = {
        'title': entry_title,
        'artist': podcast_title,
        'album': f'Podcast {podcast_title}' if podcast_title else None,
        'date': entry_date,
        'genre': 'Podcast',
    }
    if tag_dict:
        values.update(tag_dict)
    _write_id3_values(mp3_name, values)
    write_cover_art(art_filename, mp3_name)


def write_id3_tags_dict(mp3_filename, art_filename, tag_dict=None):
    _write_id3_values(mp3_filename, tag_dict or {})
    if art_filename:
        write_cover_art(art_filename, mp3_filename)
