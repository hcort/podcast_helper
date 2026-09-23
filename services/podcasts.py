"""Podcast operations shared by the CLI and web, without Flask dependencies."""
from dataclasses import dataclass, field
from pathlib import Path
from services.file_details import file_details
from threading import Lock
from urllib.parse import urlsplit
from get_driver import close_and_remove_driver
from services.download_history import DownloadHistory, mp3_snapshot, checking_download

def create_abstract_podcast_list(output_path):
    # Load media dependencies only when a podcast operation is requested.
    from register_all_podcasts import create_abstract_podcast_list as create_registry
    return create_registry(output_path)


# Providers currently share a global Selenium driver.
_driver_lock = Lock()

@dataclass
class EpisodeResult:
    url: str
    error: str | None = None
    skipped: bool = False
    files: list[dict] = field(default_factory=list)

class PodcastService:
    def __init__(self, output_path, history_path=None):
        self.output_path = Path(output_path)
        self.history_path = Path(history_path) if history_path else self.output_path / 'downloads.sqlite3'

    @staticmethod
    def _provider(registry, url):
        parsed = urlsplit(url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            raise ValueError('Introduce una URL HTTP o HTTPS válida.')
        provider = registry.get_podcast_for_url(url)
        if provider is None:
            raise ValueError('No hay un proveedor compatible con esta URL.')
        return provider

    def list_episodes(self, url):
        with _driver_lock:
            try:
                registry = create_abstract_podcast_list(str(self.output_path))
                provider = self._provider(registry, url)
                if hasattr(provider, 'disable_download_during_list'):
                    provider.disable_download_during_list()
                return provider.list_episodes(url)
            finally:
                close_and_remove_driver()

    def download_episodes(self, urls):
        results = []
        with _driver_lock:
            try:
                self.output_path.mkdir(parents=True, exist_ok=True)
                history = DownloadHistory(self.history_path)
                registry = create_abstract_podcast_list(str(self.output_path))
                for index, url in enumerate(urls, 1):
                    print(f'[{index}/{len(urls)}] Descargando {url}', flush=True)
                    try:
                        provider = self._provider(registry, url)
                        before = mp3_snapshot(self.output_path)
                        with checking_download(history) as check:
                            success = provider.get_episode(url)
                        if check.skipped:
                            results.append(EpisodeResult(url, skipped=True, files=history.episode_files(check.podcast, check.title)))
                            print('Ya descargado: se omite.', flush=True)
                            continue
                        if success is False:
                            raise RuntimeError('El proveedor no pudo descargar el episodio.')
                        after = mp3_snapshot(self.output_path)
                        changed = [path for path, stat in after.items() if before.get(path) != stat]
                        if changed:
                            history.record_files(changed, episode_url=url)
                        results.append(EpisodeResult(url, files=[file_details(path) for path in changed]))
                        print(f'Finalizado: {url}', flush=True)
                    except Exception as err:
                        results.append(EpisodeResult(url, str(err)))
                        print(f'Error - {url} - {err}', flush=True)
                return results
            finally:
                close_and_remove_driver()
