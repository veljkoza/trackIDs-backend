from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request
from flask_cors import CORS, cross_origin
from pytube import YouTube
from pydub import AudioSegment
import http.client
import mimetypes
import base64
import json
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
    ys = yt.streams.filter(only_audio=True)[0]
    ys.download("songs")
    song = AudioSegment.from_file(
        "songs\XXXTENTACION - Jocelyn Flores (Audio).mp4", "mp4")
    third_of_song = song.duration_seconds//3

    left_four_seconds = (third_of_song-2) * 1000
    right_four_seconds = (third_of_song+2) * 1000

    eight_seconds_slice = song[left_four_seconds:right_four_seconds]
    eight_seconds_slice = eight_seconds_slice.split_to_mono()[0]
    eight_seconds_slice.set_frame_rate(44100)
    eight_seconds_slice.set_sample_width(2)
    eight_seconds_slice.export("slicedsong.mp3", format="mp3")

    print("channels---------------", eight_seconds_slice.channels)
    print("frame rate---------------", eight_seconds_slice.frame_rate)
    print("sample_width---------------", eight_seconds_slice.sample_width)

    raw_data = AudioSegment.from_mp3("slicedsong.mp3")._data
    print("TYPE---------------", type(raw_data))

    raw_text = base64.b64encode(raw_data).decode('UTF-8')

    f = open("raw-text.txt", "w")
    f.write(raw_text)

    # text = base64.b64encode(raw_data)

    with open("slicedsong.mp3", "rb") as audioFile:
        text = base64.b64encode(audioFile.read())
        file = open("song.txt", "wb")
        # file.write(raw_text)
        file.close()
    print(song)
    conn = http.client.HTTPSConnection("shazam.p.rapidapi.com")

    payload = raw_text

    headers = {
        'x-rapidapi-host': "shazam.p.rapidapi.com",
        'x-rapidapi-key': "b3071fb829msha09abfd4c5a24dep19a5b1jsne43ce7980b41",
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
        'content-type': "text/plain",
        'accept': "text/plain"
    }

    conn.request("POST", "/songs/detect", payload, headers)

    res = conn.getresponse()
    data = res.read()

    print("RESPONSE--------------------------------", data.decode("utf-8"))
    # json_data = response.json()
    print("TYPE---------------", type(payload))
    return raw_text


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
    eight_seconds_slice.export("slicedsong.mp3", format="mp3")

    print("channels---------------", eight_seconds_slice.channels)
    print("frame rate---------------", eight_seconds_slice.frame_rate)
    print("sample_width---------------", eight_seconds_slice.sample_width)

    raw_data = AudioSegment.from_mp3("slicedsong.mp3")._data
    raw_text = base64.b64encode(raw_data)
    f = open("raw-text.txt", "wb")
    f.write(raw_text)
    f.close()

    # text = base64.b64encode(raw_data)

    with open("slicedsong.mp3", "rb") as audioFile:
        text = base64.b64encode(audioFile.read())
        file = open("song.txt", "wb")
        file.write(raw_text)
        file.close()
    print(song)
    url = "https://shazam.p.rapidapi.com/songs/detect"
    payload = raw_text
    headers = {
        'x-rapidapi-host': "shazam.p.rapidapi.com",
        'x-rapidapi-key': "b3071fb829msha09abfd4c5a24dep19a5b1jsne43ce7980b41",
        'content-type': "text/plain",
        'accept': "text/plain"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    return response


if __name__ == "__main__":
    app.run(debug=True)
