from flask import Flask, render_template, g
import os
from werkzeug import secure_filename

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['mp3', 'wav'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/') 
def hello_world():
    return render_template('home.html')


@app.route('/upload_page')
def upload_page():
    return render_template('upload_song.html')

@app.route('/upload_song',methods=['GET','POST'])
def process_upload


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)