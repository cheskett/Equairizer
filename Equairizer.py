
from flask import Flask, render_template, g, request, redirect, url_for, flash, app, Response
from UploadHandler import UploadHandler
from PlayHandler import PlayHandler
import json
import sqlite3
import threading
from visualizer import AudioParser
import os

app = Flask(__name__)
app.secret_key = 'this is the secret key'
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'equairizer.db')
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'songs')
app.config["DATABASE"] = DATABASE
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
uh = UploadHandler()

ph = PlayHandler()

player = AudioParser()
stop_event = threading.Event()


def connect_db():
    return sqlite3.connect(app.config["DATABASE"])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def root():
    return render_template('layout.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return render_template('uploaded.html', filename=filename)


@app.route('/upload_song', methods=['POST'])
def upload_song():
    media_file = request.files['file']
    if media_file and uh.allowed_file(media_file.filename):
        return uh.upload_file(media_file)
    else:
        flash("Unsupported File Format")
        return redirect(url_for('load_upload_page'))


@app.route('/upload_page')
def load_upload_page():
    return render_template('upload_song.html')



@app.route('/play_song')
def show_play_song_page():
	return render_template('play_song.html')

@app.route('/list_songs')
def list_songs():
	return Response(json.dumps(ph.get_song_listing()),  mimetype='application/json')

@app.route("/test_stop")
def stop_playing():
    global player
    player.pause()
    return "PAUSED"


@app.route("/test_resume")
def resume_playing():
    global player
    player.resume()
    return "RESUMED"


@app.route('/test_play')
def play_test_song():
    global stop_event
    global player
    filename = os.path.join(UPLOAD_FOLDER, 'Grizzly_Bear_-_Adelma.wav')
    player = AudioParser(filename)
    player.begin()
    import time
    # time.sleep(2)
    # e.set()
    # time.sleep(2)
    # e.clear()
    return "End"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
