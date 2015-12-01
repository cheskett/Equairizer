from flask import Flask, render_template, g, request, redirect, url_for
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

@app.route('/upload_song',methods=['POST'])
def process_upload():
	file = request.files['file']
	filename = secure_filename(file.filename)
	ext = filename.rsplit('.', 1)[len(filename.rsplit('.', 1))-1]
	if file and ext in ALLOWED_EXTENSIONS:
		print "Gottem!"
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		if ext == "wav":
			return render_template('upload_success.html')
		elif ext == "mp3":
			#ffmpeg
			return render_template('upload_success.html')
		else:
			return render_template('upload_failure.html')
	else:
		print "Nope.."
		return render_template('upload_song.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)