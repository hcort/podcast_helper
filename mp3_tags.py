import urllib

from os.path import isfile
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3


def write_cover_art(art_filename, mp3_name):
    print(f'writing {art_filename} into {mp3_name}')
    # put some ID3 tags into the mp3 file
    audio = MP3(mp3_name, ID3=ID3)
    # add ID3 tag if it doesn't exist
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
    audio["album"] = podcast_title
    audio["date"] = entry_date
    audio["genre"] = 'Podcast'
    audio.save()
