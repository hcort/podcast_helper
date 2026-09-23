"""Request-local console capture. One WSGI worker with at least four threads."""
from contextvars import ContextVar
import re
import codecs
from tempfile import TemporaryFile
import sys
from threading import Lock
from time import monotonic
from flask import abort, g, jsonify, request

_current = ContextVar('download_console', default=None)
_install_lock = Lock()


def capture(text):
    job = _current.get()
    if job is not None:
        with job['lock']:
            job['log'].seek(0, 2)
            job['log'].write(text)
            job['log'].flush()


class BinaryConsoleProxy:
    def __init__(self, original, encoding):
        self.original = original
        self.encoding = encoding or 'utf-8'

    def write(self, data):
        job = _current.get()
        if job is not None:
            with job['lock']:
                decoder = job['decoders'].setdefault(
                    id(self), codecs.getincrementaldecoder(self.encoding)(errors='replace'))
                job['log'].seek(0, 2)
                job['log'].write(decoder.decode(data))
                job['log'].flush()
        return self.original.write(data)

    def __getattr__(self, name):
        return getattr(self.original, name)


class ConsoleProxy:
    def __init__(self, original):
        self.original = original
        if hasattr(original, 'buffer'):
            self.buffer = BinaryConsoleProxy(original.buffer, getattr(original, 'encoding', None))

    def write(self, text):
        capture(text)
        return self.original.write(text)

    def flush(self):
        return self.original.flush()

    def __getattr__(self, name):
        return getattr(self.original, name)


def install(app):
    with _install_lock:
        for name in ('stdout', 'stderr'):
            stream = getattr(sys, name)
            if not isinstance(stream, ConsoleProxy):
                setattr(sys, name, ConsoleProxy(stream))
    jobs = {}
    lock = Lock()

    @app.before_request
    def begin():
        identifier = request.headers.get('X-Progress-ID')
        if not identifier or request.method != 'POST' or request.endpoint not in ('podcasts.index', 'videos.index'):
            return
        if not re.fullmatch('[0-9a-f]{32}', identifier):
            abort(400)
        with lock:
            now = monotonic()
            for key in list(jobs):
                if jobs[key]['done'] and now - jobs[key]['finished'] > 3600:
                    jobs[key]['log'].close()
                    del jobs[key]
            if identifier in jobs:
                abort(409)
            # Leave WSGI threads available to serve progress requests.
            if sum(not item['done'] for item in jobs.values()) >= 2:
                abort(429, 'Hay dos trabajos activos. Espera a que termine uno.')
            if len(jobs) >= 100:
                oldest = next((key for key, item in jobs.items() if item['done']), None)
                if oldest:
                    jobs[oldest]['log'].close()
                    del jobs[oldest]
            log = TemporaryFile(mode='w+', encoding='utf-8', newline='')
            log.write('Iniciando trabajo…\n')
            job = {'log': log, 'decoders': {}, 'done': False, 'finished': 0,
                   'results': '', 'lock': Lock()}
            jobs[identifier] = job
        g.progress_job = job
        g.progress_token = _current.set(job)

    @app.teardown_request
    def finish(error):
        job = getattr(g, 'progress_job', None)
        if job is not None:
            with job['lock']:
                if error:
                    job['log'].seek(0, 2)
                    job['log'].write(f'Error: {error}\n')
                job['done'] = True
                job['finished'] = monotonic()
            _current.reset(g.progress_token)
            del g.progress_job
            del g.progress_token

    @app.get('/progress/<identifier>')
    def progress(identifier):
        with lock:
            job = jobs.get(identifier)
        if job is None:
            abort(404)
        with job['lock']:
            try:
                offset = int(request.args.get('offset', '0'))
                if offset < 0:
                    raise ValueError
                job['log'].seek(offset)
                text = job['log'].read(65536)
                next_offset = job['log'].tell()
                more = bool(job['log'].read(1))
            except (ValueError, OSError, UnicodeError):
                abort(400)
            response = jsonify(log=text, offset=next_offset, more=more,
                               done=job['done'], results=job['results'])
        response.headers['Cache-Control'] = 'no-store'
        return response


def publish_results(html):
    job = _current.get()
    if job is not None:
        with job['lock']:
            job['results'] = html
