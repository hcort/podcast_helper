import os
import random
import site
import string

from flask import Flask, render_template, request, send_from_directory, Blueprint

from get_driver import close_and_remove_driver
from register_all_podcasts import create_abstract_podcast_list
from utils import read_config_object, zip_folder

app = Flask(__name__)
app.static_folder = os.path.join(os.getcwd(), 'output')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        random_output = ''.join(random.choices(string.ascii_lowercase, k=10))
        output_path_def = os.path.join(app.static_folder, random_output)
        all_podcasts = create_abstract_podcast_list(output_path_def)
        all_lines = request.form.get('podcast_list', '').split()
        if request.form.get('list_podcast', None) == 'List podcast':
            pass  # do something
        elif request.form.get('get_episode', None) == 'Get episode':
            for line in all_lines:
                all_podcasts.get_podcast_for_url(line).get_episode(line)
            zipfile = zip_folder(app.static_folder, random_output)
            close_and_remove_driver()
            return send_from_directory(app.static_folder, zipfile)# , mimetype='application/zip')
        else:
            return 'Invalid option'
        return 'OK'


if __name__ == '__main__':
    app.run(debug=True)
