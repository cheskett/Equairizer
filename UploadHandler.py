from flask import Flask, current_app as app, redirect, url_for
from werkzeug import secure_filename
from subprocess import call
import os

ALLOWED_EXTENSIONS = ['aac', 'ogg', 'wav', 'mp3', 'm4a']


class UploadHandler:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @staticmethod
    def convert_file(filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        wavfile = filename.split(".")[0] + ".wav"
        print filename
        print wavfile
        call(["ffmpeg", "-y", "-i", filename, "-ar", "44100", "-ac", "1", wavfile])
        os.remove(filename)

    @staticmethod
    def upload_file(media_file):
        filename = secure_filename(media_file.filename)
        media_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        UploadHandler.convert_file(filename)
        return redirect(url_for('uploaded_file',
                                filename=filename))

    def __init__(self):
        pass
