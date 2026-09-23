"""Persistent download history using SQLite.

Import an existing library with:
    python -m services.download_history OUTPUT_FOLDER
"""
import argparse
import json
import sqlite3
from contextlib import closing, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class DownloadCheck:
    history: object
    skipped: bool = False
    podcast: str | None = None
    title: str | None = None


_active_check = ContextVar('download_check', default=None)


@contextmanager
def checking_download(history):
    check = DownloadCheck(history)
    token = _active_check.set(check)
    try:
        yield check
    finally:
        _active_check.reset(token)


def already_downloaded(podcast, title):
    """Providers call this after reading names and before requesting audio."""
    check = _active_check.get()
    if check is None:
        return False
    check.podcast, check.title = podcast, title
    check.skipped = check.history.contains_episode(podcast, title)
    return check.skipped


def read_metadata(filename):
    """Validate the MPEG audio and retain identification fields, not artwork."""
    from mutagen.mp3 import MP3

    audio = MP3(filename)
    tags = audio.tags or {}

    def value(key):
        frame = tags.get(key)
        return str(frame) if frame is not None else None

    album = value('TALB')
    podcast = album[len('Podcast '):] if album and album.startswith('Podcast ') else None
    return {
        'podcast': podcast or value('TPE1') or value('TPE2') or album,
        'title': value('TIT2') or Path(filename).stem,
        'album': value('TALB'),
        'published_at': value('TDRC') or value('TYER'),
        'track_number': value('TRCK'),
        'source_url': value('WOAS'),
        'youtube_id': value('TXXX:YouTube ID'),
        'duration_seconds': audio.info.length,
    }


class DownloadHistory:
    def __init__(self, filename):
        self.filename = Path(filename)
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('''CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY,
                file_path TEXT NOT NULL UNIQUE,
                podcast TEXT, title TEXT NOT NULL, downloaded_at TEXT NOT NULL,
                date_source TEXT NOT NULL,
                album TEXT, published_at TEXT, track_number TEXT,
                source_url TEXT, youtube_id TEXT, duration_seconds REAL,
                file_size INTEGER NOT NULL,
                episode_urls TEXT NOT NULL DEFAULT '[]'
            )''')
            db.execute('CREATE INDEX IF NOT EXISTS downloads_episode ON downloads(podcast, title)')

    def _connect(self):
        return sqlite3.connect(self.filename, timeout=30)

    def contains_episode(self, podcast, title):
        if not podcast or not title:
            return False
        with closing(self._connect()) as db:
            return db.execute('SELECT 1 FROM downloads WHERE podcast = ? AND title = ?',
                              (podcast, title)).fetchone() is not None

    def episode_files(self, podcast, title):
        with closing(self._connect()) as db:
            db.row_factory = sqlite3.Row
            records = [dict(row) for row in db.execute(
                'SELECT * FROM downloads WHERE podcast = ? AND title = ?', (podcast, title))]
        for record in records:
            record['available'] = Path(record['file_path']).is_file()
        return records

    def list_downloads(self):
        with closing(self._connect()) as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute(
                'SELECT * FROM downloads ORDER BY podcast COLLATE NOCASE, title COLLATE NOCASE, id')]

    def delete_download(self, record_id):
        """Delete only the selected database row; never touch the media file."""
        with closing(self._connect()) as db, db:
            return db.execute('DELETE FROM downloads WHERE id = ?', (record_id,)).rowcount > 0

    def record_files(self, filenames, episode_url=None, imported=False):
        # Parse every file before committing to avoid recording partial results.
        records = build_records(filenames, imported)
        with closing(self._connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            for record in records:
                previous = db.execute('SELECT episode_urls FROM downloads WHERE file_path = ?',
                                      (record['file_path'],)).fetchone()
                urls = set(json.loads(previous[0])) if previous else set()
                urls.update(url for url in (episode_url, record['source_url']) if url)
                record['episode_urls'] = json.dumps(sorted(urls), ensure_ascii=False)
                db.execute('''INSERT INTO downloads (
                    file_path, podcast, title, downloaded_at, date_source, album,
                    published_at, track_number, source_url, youtube_id, duration_seconds, file_size, episode_urls
                ) VALUES (:file_path, :podcast, :title, :downloaded_at, :date_source,
                    :album, :published_at, :track_number, :source_url, :youtube_id,
                    :duration_seconds, :file_size, :episode_urls)
                ON CONFLICT(file_path) DO UPDATE SET
                    podcast=excluded.podcast, title=excluded.title,
                    album=excluded.album, published_at=excluded.published_at,
                    track_number=excluded.track_number, source_url=excluded.source_url,
                    youtube_id=excluded.youtube_id, duration_seconds=excluded.duration_seconds,
                    file_size=excluded.file_size, episode_urls=excluded.episode_urls''', record)
        return len(records)


def build_records(filenames, imported=False):
    records = []
    for filename in filenames:
        path = Path(filename).resolve()
        metadata = read_metadata(path)
        stat = path.stat()
        date = datetime.fromtimestamp(stat.st_mtime, timezone.utc) if imported else datetime.now(timezone.utc)
        records.append(dict(metadata, file_path=str(path), file_size=stat.st_size,
                            downloaded_at=date.isoformat(),
                            date_source='file_mtime' if imported else 'download'))
    return records


def mp3_snapshot(folder):
    return {path.resolve(): (path.stat().st_mtime_ns, path.stat().st_size)
            for path in Path(folder).rglob('*') if path.is_file() and path.suffix.lower() == '.mp3'}


def main():
    parser = argparse.ArgumentParser(description='Importar MP3 existentes al historial SQLite.')
    parser.add_argument('folder', type=Path)
    parser.add_argument('--database', type=Path)
    args = parser.parse_args()
    if not args.folder.is_dir():
        parser.error('La carpeta de MP3 no existe.')
    history = DownloadHistory(args.database or args.folder / 'downloads.sqlite3')
    count = 0
    for path in mp3_snapshot(args.folder):
        try:
            count += history.record_files([path], imported=True)
        except Exception as err:
            print(f'No se pudo importar {path}: {err}')
    print(f'MP3 procesados: {count}. Historial: {history.filename}')


if __name__ == '__main__':
    main()
