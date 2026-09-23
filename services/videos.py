"""Video batch downloads independent of Flask."""
from dataclasses import dataclass, field
from pathlib import Path
from services.file_details import file_details
from get_youtube_video import download_youtube_video


@dataclass
class VideoResult:
    url: str
    path: Path | None = None
    error: str | None = None
    files: list[dict] = field(default_factory=list)


class VideoService:
    def __init__(self, output_path):
        self.output_path = Path(output_path)

    def download_videos(self, urls):
        results = []
        for index, url in enumerate(urls, 1):
            print(f'[{index}/{len(urls)}] Descargando {url}', flush=True)
            try:
                path = download_youtube_video(url, self.output_path)
                results.append(VideoResult(url, path=path, files=[file_details(path)]))
                print(f'Guardado: {path}', flush=True)
            except Exception as error:
                results.append(VideoResult(url, error=str(error)))
                print(f'Error - {url} - {error}', flush=True)
        return results
