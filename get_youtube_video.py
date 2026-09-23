"""Download YouTube videos with their audio using yt-dlp."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import yt_dlp

from get_youtube_audio_2 import (
    SUPPORTED_COOKIE_BROWSERS,
    _find_deno,
    _find_ffmpeg,
    is_youtube_url,
)


def _video_format(max_height: int | None) -> str:
    """Build a format selector that favours MP4-compatible video and audio."""
    height_filter = f"[height<={max_height}]" if max_height is not None else ""
    return (
        f"bestvideo[ext=mp4]{height_filter}+bestaudio[ext=m4a]/"
        f"best[ext=mp4]{height_filter}/best{height_filter}"
    )


def _result_path(info: dict, downloader: yt_dlp.YoutubeDL, candidates: list[Path]) -> Path:
    """Find the final file produced by yt-dlp and its post-processors."""
    info_path = info.get("filepath")
    if info_path:
        candidates.append(Path(info_path))

    requested_downloads = info.get("requested_downloads") or []
    candidates.extend(
        Path(download["filepath"])
        for download in requested_downloads
        if download.get("filepath")
    )

    prepared_path = Path(downloader.prepare_filename(info))
    candidates.extend((prepared_path.with_suffix(".mp4"), prepared_path))
    for candidate in reversed(candidates):
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "yt-dlp finished without producing the expected video file: "
        f"{prepared_path.with_suffix('.mp4')}"
    )


def download_youtube_video(
    url: str,
    output_path: str | os.PathLike[str],
    *,
    max_height: int | None = None,
    ffmpeg_location: str | os.PathLike[str] | None = None,
    cookies_from_browser: str | None = None,
    user_agent: str | None = None,
) -> Path:
    """Download one YouTube video with audio and return the resulting path.

    The best available MP4-compatible streams are selected and merged into an
    MP4 file. ``max_height`` can be used to cap the resolution (for example,
    ``1080``). FFmpeg is needed when video and audio are separate streams.
    """
    if not is_youtube_url(url):
        raise ValueError(f"Not a YouTube URL: {url}")
    if max_height is not None and max_height <= 0:
        raise ValueError("max_height must be a positive integer")

    output_root = Path(output_path).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    output_template = str(
        output_root
        / "%(title).180B.%(ext)s"
    )
    final_paths: list[Path] = []

    def remember_postprocessed_path(status: dict) -> None:
        if status.get("status") != "finished":
            return
        filepath = status.get("info_dict", {}).get("filepath")
        if filepath:
            final_paths.append(Path(filepath))

    ydl_options = {
        "format": _video_format(max_height),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "overwrites": False,
        "outtmpl": output_template,
        "windowsfilenames": os.name == "nt",
        "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True}],
        "postprocessor_hooks": [remember_postprocessed_path],
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
        return _result_path(info, downloader, final_paths)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Descarga un vídeo de YouTube con audio en formato MP4."
    )
    parser.add_argument("url", help="URL del vídeo de YouTube")
    parser.add_argument("output_path", help="Carpeta donde guardar el vídeo")
    parser.add_argument(
        "--max-height",
        type=int,
        help="Resolución vertical máxima (por ejemplo, 1080)",
    )
    parser.add_argument(
        "--cookies-from-browser",
        choices=sorted(SUPPORTED_COOKIE_BROWSERS),
        help="Usa las cookies de este navegador si YouTube exige autenticación",
    )
    parser.add_argument("--ffmpeg-location", help="Ruta a FFmpeg o a su carpeta")
    parser.add_argument("--user-agent", help="Cabecera User-Agent personalizada")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        video_path = download_youtube_video(
            args.url,
            args.output_path,
            max_height=args.max_height,
            ffmpeg_location=args.ffmpeg_location,
            cookies_from_browser=args.cookies_from_browser,
            user_agent=args.user_agent,
        )
    except (ValueError, FileNotFoundError, yt_dlp.utils.DownloadError) as error:
        print(f"No se pudo descargar el vídeo: {error}")
        return 1
    print(video_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
