from flask import Flask, app

ALLOWED_EXTENSIONS = ['aac', 'ogg', 'wav', 'mp3']


class UploadHandler:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def __init__(self):
        pass
