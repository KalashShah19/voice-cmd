from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import tempfile
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/record', methods=['POST'])
def record_audio():
    temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    audio_file_path = temp_audio_file.name
    temp_audio_file.close()
    print(audio_file_path)

    duration = request.form.get('duration', 5)  # Default recording duration is 5 seconds

    # Use sox to record audio
    cmd = ['sox', '-d', '-t', 'wav', audio_file_path, 'trim', '0', str(duration)]
    subprocess.run(cmd)

    return jsonify({'audio_file_path': audio_file_path})

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'audio_file_path' not in request.form:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file_path = request.form['audio_file_path']

    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return jsonify({'transcription': text}), 200
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Speech recognition service error: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
