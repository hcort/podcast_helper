"""Video download form."""
from pathlib import Path
from flask import Blueprint, current_app, render_template, request
from services.videos import VideoService
from utils import read_config_object

bp = Blueprint('videos', __name__)


@bp.route('/videos', methods=['GET', 'POST'])
def index():
    context = {'video_urls': request.form.get('video_urls', '')}
    if request.method == 'POST':
        try:
            urls = context['video_urls'].split()
            if not urls:
                raise ValueError('Introduce al menos una URL de YouTube.')
            folder = current_app.config.get('VIDEO_FOLDER') or read_config_object().get('video_folder')
            if not isinstance(folder, str) or not folder.strip():
                raise ValueError('Configura video_folder en res/config.json.')
            output = Path(folder).expanduser().resolve()
            context['results'] = VideoService(output).download_videos(urls)
            context['saved_folder'] = str(output)
        except Exception as error:
            context['error'] = str(error)
            return render_template('videos.html', **context), 400
    return render_template('videos.html', **context)
