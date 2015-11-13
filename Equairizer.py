from flask import Flask, render_template, g, request, redirect, url_for, flash, app, Response
from UploadHandler import UploadHandler
from PlayHandler import PlayHandler
import json
import eyed3
import sqlite3
from werkzeug import secure_filename
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
    song_name = request.form['songName']
    artist = request.form['artist']
    media_file = request.files['file']
    filename = secure_filename(media_file.filename)
    media_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if(song_name is None or song_name == ""):
    	if(filename.split('.')[len(filename.split('.'))-1].lower() == 'mp3'):
    		# It's an MP3, so grab the name and artist from that!
            audiofile = eyed3.load(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print audiofile.tag.title
            print audiofile.tag.artist
            
            song_name = audiofile.tag.title
            artist = audiofile.tag.artist
    	else: #No data? Reject
            flash("Unsupported File Format")
            return render_template('upload_song.html')

    if media_file and uh.allowed_file(media_file.filename):
        cur = g.db.cursor()
        selectQuery = 'SELECT id FROM songs WHERE name="{}"'.format(song_name)
        
        cur.execute(selectQuery)
        print 'Name: {}'.format(song_name)
        row = cur.fetchone()
        if(row is None): #The row didn't exist, so insert it
        	insertQuery = 'INSERT INTO songs (name,artist) VALUES (?,?)'
        	cur.execute(insertQuery,[song_name,artist])
        	g.db.commit()
        	id = cur.lastrowid
        else: #Song name exists already, overwrite it
            id = row[0]
            print "Song Existed: {}".format(id)
        cur.close()

        return uh.upload_file(filename,id)
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


@app.route('/play/<song>/')
def play_test_song(song=None):
    global stop_event
    global player
    filename = os.path.join(UPLOAD_FOLDER, '{}.wav'.format(song))
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
