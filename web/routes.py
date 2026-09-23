"""Form handling and file delivery."""
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from flask import Blueprint, current_app, render_template, request, send_file
from services.podcasts import PodcastService
from utils import read_config_object
from web.progress import publish_results

bp = Blueprint('podcasts', __name__)


def output_folder():
    configured = current_app.config.get('OUTPUT_FOLDER')
    return Path(configured or read_config_object()['output_folder']).resolve()


def temporary_download(urls, context):
    temporary = TemporaryDirectory(prefix='podcast-helper-')
    try:
        root = Path(temporary.name)
        folder = root / 'episodes'
        context['results'] = PodcastService(
            folder, history_path=output_folder() / 'downloads.sqlite3'
        ).download_episodes(urls)
        if not any(path.is_file() for path in folder.rglob('*')):
            temporary.cleanup()
            return None
        errors = [f'{result.url}: {result.error}' for result in context['results'] if result.error]
        if errors:
            (folder / 'errores.txt').write_text('\n'.join(errors), encoding='utf-8')
        print('Comprimiendo archivos…', flush=True)
        publish_results(render_template('results.html', results=context['results'], temporary=True))
        archive = shutil.make_archive(str(root / 'podcasts'), 'zip', folder)
        response = send_file(archive, mimetype='application/zip', as_attachment=True, download_name='podcasts.zip')
        # Ensure Werkzeug closes the file before removing it (also on Windows).
        response.direct_passthrough = False
        response.call_on_close(temporary.cleanup)
        return response
    except BaseException:
        temporary.cleanup()
        raise


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/podcasts', methods=['GET', 'POST'])
def index():
    podcast_url = request.form.get('podcast_url', '').strip()
    episode_text = request.form.get('episode_urls', '')
    zip_download = request.form.get('zip_download') == 'on'
    context = dict(podcast_url=podcast_url, episode_text=episode_text, zip_download=zip_download)
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            if action == 'list':
                with TemporaryDirectory(prefix='podcast-list-') as folder:
                    episodes = PodcastService(folder).list_episodes(podcast_url)
                context.update(episode_text='\n'.join(episodes or []), listed=True)
            elif action == 'download':
                urls = episode_text.split()
                if not urls:
                    raise ValueError('Introduce al menos un enlace de episodio.')
                if zip_download:
                    response = temporary_download(urls, context)
                    if response is not None:
                        return response
                else:
                    output = output_folder()
                    context['results'] = PodcastService(output).download_episodes(urls)
                    context['saved_folder'] = str(output)
            else:
                raise ValueError('Acción desconocida.')
        except Exception as err:
            context['error'] = str(err)
            return render_template('index.html', **context), 400
    return render_template('index.html', **context)
