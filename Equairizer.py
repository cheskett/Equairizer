from flask import Flask, render_template, g

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/upload_page')
def upload_song():
    return render_template('upload_song.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)