from flask import Flask, render_template, request, jsonify
import os
import time
import speech_recognition as sr

app = Flask(__name__)

# Global variable to store recorded audio
recorded_audio_path = None

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    global recorded_audio_path
    audio_file = request.files['audio']
    audio_dir = 'recorded_audio'
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    filename = f'recorded_audio_{int(time.time())}.wav'
    filepath = os.path.join(audio_dir, filename)
    # audio_file.save(filepath)
    recorded_audio_path = filepath
    print("Recoding Sucess")
    print("File Path = " + recorded_audio_path)
    recognize_speech()
    return 'Audio recorded successfully'

@app.route('/recognize_speech')
def recognize_speech():
    print("Recognizing")
    global recorded_audio_path
    if recorded_audio_path is None:
        return 'No audio recorded', 400

    recognizer = sr.Recognizer()
    with sr.AudioFile(recorded_audio_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        print("Command = " + text)
        return jsonify({'transcription': text}), 200
    except sr.UnknownValueError:
        print("Error")
        return jsonify({'error': 'Could not understand audio'}), 400
    except sr.RequestError as e:
        print("Error : " + e)
        return jsonify({'error': f'Speech recognition service error: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
