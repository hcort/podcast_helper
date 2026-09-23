"""Read presentation metadata without changing the download outcome."""
from datetime import datetime, timezone
from pathlib import Path


def file_details(filename):
    path = Path(filename).resolve()
    detail = {'file_path': str(path), 'title': path.stem, 'available': path.is_file()}
    if not detail['available']:
        return detail
    stat = path.stat()
    detail.update(file_size=stat.st_size,
                  downloaded_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat())
    try:
        if path.suffix.lower() == '.mp3':
            from services.download_history import read_metadata
            detail.update(read_metadata(path))
        else:
            from mutagen import File
            media = File(path, easy=True)
            if media:
                detail['duration_seconds'] = getattr(media.info, 'length', None)
                for source, target in [('title', 'title'), ('artist', 'podcast'), ('date', 'published_at')]:
                    values = (media.tags or {}).get(source)
                    if values:
                        detail[target] = str(values[0])
    except Exception:
        # Missing optional tags must not mark a completed download as failed.
        pass
    return detail
