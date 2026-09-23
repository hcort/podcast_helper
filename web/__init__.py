"""Flask application factory."""
import os
from flask import Flask

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        OUTPUT_FOLDER=os.environ.get('PODCAST_OUTPUT_FOLDER'),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if config:
        app.config.update(config)
    from web.routes import bp
    app.register_blueprint(bp)
    return app
