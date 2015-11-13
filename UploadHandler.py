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
    def convert_file(filename,id):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        wavfile = os.path.join(app.config['UPLOAD_FOLDER'],"{}.wav".format(id))
        print filename
        print wavfile
        call(["ffmpeg", "-y", "-i", filename, "-ar", "44100", "-ac", "1", wavfile])
        os.remove(filename)

    @staticmethod
    def upload_file(filename,id):
        
        UploadHandler.convert_file(filename,id)
        return redirect(url_for('uploaded_file',
                                filename=filename))

    def __init__(self):
        pass
