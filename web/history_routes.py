"""Browse and remove records from the shared podcast download history."""
import secrets
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from services.download_history import DownloadHistory
from web.routes import output_folder

bp = Blueprint('history', __name__)


def history_store():
    return DownloadHistory(output_folder() / 'downloads.sqlite3')


@bp.get('/history')
def index():
    if 'history_csrf' not in session:
        session['history_csrf'] = secrets.token_urlsafe(32)
    groups = {}
    for record in history_store().list_downloads():
        author = record['podcast'] or 'Sin autor'
        groups.setdefault(author, []).append(record)
    return render_template('history.html', groups=groups,
                           total=sum(len(records) for records in groups.values()),
                           csrf_token=session['history_csrf'])


@bp.post('/history/<int:record_id>/delete')
def delete(record_id):
    expected = session.get('history_csrf', '')
    supplied = request.form.get('csrf_token', '')
    if not expected or not secrets.compare_digest(expected, supplied):
        abort(403)
    if not history_store().delete_download(record_id):
        abort(404)
    flash('Registro eliminado de la base de datos. El archivo se conserva.')
    return redirect(url_for('history.index'), code=303)
