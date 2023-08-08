import os
import moviepy.editor as mp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3


def mp4_to_mp3(path, mp4_name, extension='mp4', delete_mp4=False):
    mp4_file = os.path.join(path, f'{mp4_name}.{extension}')
    mp3_file = os.path.join(path, f'{mp4_name}.mp3')
    clip = mp.AudioFileClip(mp4_file)
    clip.write_audiofile(mp3_file)
    if delete_mp4:
        os.remove(mp4_file)
    return mp3_file


def write_cover_art(art_filename, mp3_name):
    print(f'writing {art_filename} into {mp3_name}')
    audio = MP3(mp3_name, ID3=ID3)
    try:
        audio.add_tags()
    except Exception as ex:
        pass
    try:
        mime = 'image/png' if art_filename.endswith('png') else 'image/jpeg'
        file = open(art_filename, 'rb')
        data = file.read()
        audio.tags.add(
            APIC(
                encoding=3,  # 3 is for utf-8
                mime=mime,  # image/jpeg or image/png
                type=3,  # 3 is for the cover image
                desc=u'Cover',
                data=data
            )
        )
    except Exception as ex:
        pass
    audio.save()


# writes some basic ID3 tags to the mp3 file
def write_mp3_tags(entry_title, podcast_title, entry_date, art_filename, mp3_name):
    write_cover_art(art_filename, mp3_name)
    audio = EasyID3(mp3_name)
    audio["title"] = entry_title
    audio["artist"] = podcast_title
    audio["album"] = f'Podcast {podcast_title}'
    audio["date"] = entry_date
    audio["genre"] = 'Podcast'
    audio.save()


def write_id3_tags_dict(mp3_filename, art_filename, tag_dict={}):
    from mutagen.id3 import ID3NoHeaderError
    from mutagen.easyid3 import EasyID3
    from mutagen import File
    try:
        meta = EasyID3(mp3_filename)
    except ID3NoHeaderError:
        meta = File(mp3_filename, easy=True)
        meta.add_tags()
    for tag in tag_dict:
        try:
            meta[tag] = tag_dict[tag]
        except Exception as err:
            # mp3 and mp4 files have different sets of valid tags
            print(err)
    meta.save()
    if art_filename:
        write_cover_art(mp3_filename, art_filename)
