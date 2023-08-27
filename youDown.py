from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
from pytube import Playlist
from moviepy.editor import *

app = Flask(__name__)

current_status = {"total": 0, "current": 0, "current_title": ""}

def download_and_convert_playlist(url, download_path="."):
     
    global current_status
    current_status["completed"] = False  # Setzen Sie dies zu Beginn des Downloads zurück
    playlist = Playlist(url)
    current_status["total"] = len(playlist.videos)

    for index, video in enumerate(playlist.videos):
        current_status["current"] = index + 1
        current_status["current_title"] = video.title.replace(":", "_").replace(" ", "")
         
        video_stream = video.streams.filter(file_extension='mp4').first()
        video_file = video_stream.download(output_path=download_path, filename_prefix='temp_')
        
        # Konvertiert das heruntergeladene Video in MP3
        audio = AudioFileClip(video_file)
        audio.write_audiofile(os.path.join(download_path, current_status["current_title"] + ".mp3"))
        
        # Löscht die temporäre Videodatei
        os.remove(video_file)
        current_status["completed"] = True  # Setzen Sie dies am Ende des Downloads

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        download_and_convert_playlist(url, 'downloads')  # Wir speichern die MP3-Dateien im "downloads"-Ordner
        return 'Download und Konvertierung abgeschlossen!'
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    return jsonify(current_status)

@app.route('/downloads/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory('downloads', filename)

if __name__ == "__main__":
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
