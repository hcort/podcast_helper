"""Flask application factory."""
import os
import secrets
from flask import Flask

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32),
        OUTPUT_FOLDER=os.environ.get('PODCAST_OUTPUT_FOLDER'),
        VIDEO_FOLDER=os.environ.get('VIDEO_FOLDER'),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if config:
        app.config.update(config)
    from web.routes import bp
    app.register_blueprint(bp)
    from web.video_routes import bp as video_bp
    app.register_blueprint(video_bp)
    from web.history_routes import bp as history_bp
    app.register_blueprint(history_bp)
    from web.progress import install
    install(app)
    return app
