from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request
from flask_cors import CORS, cross_origin
from pytube import YouTube
from pydub import AudioSegment
import base64
AudioSegment.converter = "C:\\ffmpeg\\bin\\ffmpeg.exe"

app = Flask(__name__)
cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r> % self.id'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<ytlink>',
           methods=['GET', 'POST', 'PUT'])
@cross_origin()
def returnLink(ytlink):
    link = request.args.get("ytlink")
    yt = YouTube("https://www.youtube.com/"+ytlink)
    print(ytlink)
    print(yt.streams.filter(only_audio=True))
    ys = yt.streams.filter(only_audio=True)[0]
    ys.download("songs")
    # song = AudioSegment.from_file("Pelada A mí me juzgan por ser mujer.mp4","mp4")

    # first_10_seconds = song[:ten_seconds]
    # print("SOOOONG" % first_10_seconds)
    # with open("Pelada A mí me juzgan por ser mujer.mp4", "rb") as audioFile:
    #     text = base64.b64encode(audioFile.read())
    #     file = open("song.txt", "wb")
    # file.write(text)
    # file.close()
    return "nice"
    # print(link)


@app.route("/pydub")
def editSong():
    song = AudioSegment.from_file(
        "songs\XXXTENTACION - Jocelyn Flores (Audio).mp4", "mp4")
    third_of_song = song.duration_seconds//3

    left_four_seconds = (third_of_song-2) * 1000
    right_four_seconds = (third_of_song+2) * 1000
    eight_seconds_slice = song[left_four_seconds:right_four_seconds]
    eight_seconds_slice = eight_seconds_slice.split_to_mono()[0]
    # eight_seconds_slice.set_channels(1)
    eight_seconds_slice.set_frame_rate(44100)
    eight_seconds_slice.set_sample_width(2)
    eight_seconds_slice.export("slicedsong.mp3",format="mp3")

    print("channels---------------", eight_seconds_slice.channels)
    print("frame rate---------------", eight_seconds_slice.frame_rate)
    print("sample_width---------------", eight_seconds_slice.sample_width)


    raw_data = AudioSegment.from_mp3("slicedsong.mp3")._data
    raw_text = base64.b64encode(raw_data)
    f = open("raw-text.txt","wb")
    f.write(raw_text)
    f.close()

    # text = base64.b64encode(raw_data)

    with open("slicedsong.mp3", "rb") as audioFile:
        text = base64.b64encode(audioFile.read())
        file = open("song.txt", "wb")
        file.write(raw_text)
        file.close()
    print(song)
    return raw_text


if __name__ == "__main__":
    app.run(debug=True)
