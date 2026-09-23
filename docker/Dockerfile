FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    MOZ_HEADLESS=1 FIREFOX_BINARY=/usr/bin/firefox-esr \
    PODCAST_OUTPUT_FOLDER=/app/output
RUN apt-get update && apt-get install -y --no-install-recommends firefox-esr ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
COPY docker/requirements.txt ./docker/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r docker/requirements.txt
RUN useradd --create-home podcast && mkdir /app/output && chown podcast:podcast /app/output
COPY --chown=podcast:podcast *.py ./
COPY --chown=podcast:podcast services/ ./services/
COPY --chown=podcast:podcast web/ ./web/
COPY --chown=podcast:podcast res/config.json ./res/config.json
USER podcast
# Cache the Linux driver at build time; no Windows executable is copied.
RUN python -c "from webdriver_manager.firefox import GeckoDriverManager; GeckoDriverManager().install()"
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "0", "flask_entry_point:app"]
