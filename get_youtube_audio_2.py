"""Download YouTube audio as a tagged MP3 using yt-dlp."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

from abstract_podcast import AbstractPodcast
from mp3_tags import write_mp3_tags


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
SUPPORTED_COOKIE_BROWSERS = {
    "brave", "chrome", "chromium", "edge", "firefox", "opera", "vivaldi", "whale"
}


def is_youtube_url(url: str) -> bool:
    """Return whether *url* points to a supported YouTube hostname."""
    hostname = (urlparse(url).hostname or "").lower()
    return hostname in YOUTUBE_HOSTS or hostname.endswith(".youtube.com")


def _date_from_info(info: dict) -> str | None:
    upload_date = info.get("upload_date")
    if not upload_date or len(upload_date) != 8:
        return upload_date
    return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"


def _find_ffmpeg(ffmpeg_location: str | os.PathLike[str] | None) -> str | None:
    if ffmpeg_location is not None:
        return os.fspath(ffmpeg_location)
    if shutil.which("ffmpeg"):
        return None
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError):
        return None


def _find_deno() -> str | None:
    executable = shutil.which("deno")
    if executable:
        return executable
    venv_executable = Path(sys.executable).parent / "deno.exe"
    return str(venv_executable) if venv_executable.is_file() else None


def download_youtube_audio(
    url: str,
    output_path: str | os.PathLike[str],
    *,
    ffmpeg_location: str | os.PathLike[str] | None = None,
    cookies_from_browser: str | None = None,
    user_agent: str | None = None,
) -> Path:
    """Download one YouTube video, convert it to MP3 and return its path.

    yt-dlp writes the thumbnail and embeds it as cover art.  FFmpeg is required
    for MP3 conversion; ``ffmpeg_location`` may point to its executable or
    containing directory when it is not available on PATH. If YouTube requests
    authentication, ``cookies_from_browser`` can name a browser supported by
    yt-dlp (for example, ``"firefox"`` or ``"edge"``).
    """
    if not is_youtube_url(url):
        raise ValueError(f"Not a YouTube URL: {url}")

    output_root = Path(output_path).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    output_template = str(
        output_root / "%(uploader,channel|Unknown channel)s" / "%(title).180B [%(id)s].%(ext)s"
    )
    ydl_options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": output_template,
        "windowsfilenames": os.name == "nt",
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail"},
        ],
    }
    resolved_ffmpeg = _find_ffmpeg(ffmpeg_location)
    if resolved_ffmpeg is not None:
        ydl_options["ffmpeg_location"] = resolved_ffmpeg
    deno_executable = _find_deno()
    if deno_executable is not None:
        ydl_options["js_runtimes"] = {"deno": {"path": deno_executable}}
    if cookies_from_browser is not None:
        browser = cookies_from_browser.lower()
        if browser not in SUPPORTED_COOKIE_BROWSERS:
            raise ValueError(f"Unsupported cookie browser: {cookies_from_browser}")
        ydl_options["cookiesfrombrowser"] = (browser, None, None, None)
    if user_agent is not None:
        ydl_options["http_headers"] = {"User-Agent": user_agent}

    with yt_dlp.YoutubeDL(ydl_options) as downloader:
        info = downloader.extract_info(url, download=True)
        source_path = Path(downloader.prepare_filename(info))

    mp3_path = source_path.with_suffix(".mp3")
    if not mp3_path.is_file():
        raise FileNotFoundError(f"yt-dlp did not produce the expected MP3: {mp3_path}")
    artist = info.get("artist") or info.get("creator") or info.get("uploader") or info.get("channel")
    title = info.get("track") or info.get("title")
    write_mp3_tags(
        entry_title=title,
        podcast_title=artist,
        entry_date=_date_from_info(info),
        art_filename=None,
        mp3_name=mp3_path,
        tag_dict={
            "album": info.get("album") or info.get("series") or f"Podcast {artist}",
            "albumartist": artist,
            "webpage_url": info.get("webpage_url") or url,
            "channel_url": info.get("channel_url"),
            "description": info.get("description"),
            "youtube_id": info.get("id"),
            "channel_id": info.get("channel_id"),
            "uploader_id": info.get("uploader_id"),
            "language": info.get("language"),
            "copyright": info.get("license"),
            "length": round(info["duration"] * 1000) if info.get("duration") else None,
            "tracknumber": info.get("track_number"),
            "discnumber": info.get("disc_number"),
            "series": info.get("series"),
            "season_number": info.get("season_number"),
            "episode_number": info.get("episode_number"),
            "youtube_categories": info.get("categories"),
            "youtube_tags": info.get("tags"),
        },
    )
    return mp3_path


def list_videos_from_playlist(playlist_url: str) -> list[str]:
    """List video URLs without downloading the playlist entries."""
    options = {"extract_flat": True, "quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(playlist_url, download=False)
    entries = info.get("entries") if info else None
    if not entries:
        return [playlist_url]
    return [entry.get("webpage_url") or entry["url"] for entry in entries if entry]


class YoutubePodcast2(AbstractPodcast):
    """``AbstractPodcast`` adapter backed by yt-dlp."""

    def __init__(
        self,
        output_path: str | None = None,
        ffmpeg_location: str | None = None,
        cookies_from_browser: str | None = None,
        user_agent: str | None = None,
    ):
        self._output_path = output_path
        self._ffmpeg_location = ffmpeg_location
        self._cookies_from_browser = cookies_from_browser
        self._user_agent = user_agent

    def check_url(self, url_to_check: str) -> bool:
        return is_youtube_url(url_to_check)

    def list_episodes(self, start_url: str) -> list[str]:
        return list_videos_from_playlist(start_url)

    def get_episode(self, episode_url: str) -> bool:
        if not self._output_path:
            raise FileNotFoundError("An output path must be configured")
        try:
            download_youtube_audio(
                episode_url,
                self._output_path,
                ffmpeg_location=self._ffmpeg_location,
                cookies_from_browser=self._cookies_from_browser,
                user_agent=self._user_agent,
            )
            return True
        except yt_dlp.utils.DownloadError as error:
            print(f"Unable to download {episode_url}: {error}")
            return False

    def set_output_path(self, output_path: str):
        self._output_path = output_path
