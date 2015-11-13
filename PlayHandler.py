from flask import Flask, current_app as app, redirect, url_for, g
from werkzeug import secure_filename
from subprocess import call
import os.path


class PlayHandler:
    @staticmethod
    def get_song_listing():
        #1. Get list of songs from database
        #2. Check that each song from database has a wav in the upload folder, remove ones that don't
        c = g.db.cursor()
        selectQuery = 'SELECT * FROM songs ORDER BY id DESC'
        c.execute(selectQuery)
        songList = []
        checkList = c.fetchall()
        for id,name,artist in checkList:
            filename = os.path.join(app.config['UPLOAD_FOLDER'],'{}.wav'.format(id))
            if(os.path.isfile(filename)):
                songList.append({'id':id,'name':name,'artist':artist})
        c.close()
        return songList


    def __init__(self):
        pass
