from flask import Flask, render_template, g, request, redirect, url_for, flash
from UploadHandler import UploadHandler
from werkzeug import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'this is the secret key'
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'equairizer.db')
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'songs')
app.config["DATABASE"] = DATABASE
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
uh = UploadHandler()


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
        filename = secure_filename(media_file.filename)
        media_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))
    else:
        flash("Unsupported File Format")
        return redirect(url_for('load_upload_page'))


@app.route('/upload_page')
def load_upload_page():
    return render_template('upload_song.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
