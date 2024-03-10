from flask import Flask, render_template, request, jsonify
import os
import time
import speech_recognition as sr

app = Flask(__name__)
app = Flask(__name__, static_folder='templates/static')

# Global variable to store recorded audio
recorded_audio_path = None

@app.route('/')
def index():
    return render_template('voice.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/ai')
def ai():
    return render_template('ai.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
