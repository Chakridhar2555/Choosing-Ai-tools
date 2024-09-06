import os
import re  # Import regular expression module
import cv2
import speech_recognition as sr
from flask import Flask, render_template, request, redirect, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
from pydub import AudioSegment

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Path to save uploaded images and audio files
UPLOAD_FOLDER = 'static/uploads/'
AUDIO_FOLDER = 'static/audio/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg'}

# Check allowed file types for images
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Convert image to pencil sketch
def convert_to_sketch(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_image = cv2.bitwise_not(gray_image)
    blurred = cv2.GaussianBlur(inverted_image, (21, 21), 0)
    inverted_blurred = cv2.bitwise_not(blurred)
    sketch_image = cv2.divide(gray_image, inverted_blurred, scale=256.0)
    sketch_image_path = image_path.rsplit('.', 1)[0] + "_sketch.jpg"
    cv2.imwrite(sketch_image_path, sketch_image)
    return sketch_image_path

# Fetch YouTube Transcript and summarize it
def summarize_youtube_video(video_url):
    # Regular expression to extract the video ID from various YouTube URL formats
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)

    if not video_id_match:
        raise ValueError("Invalid YouTube URL format.")

    video_id = video_id_match.group(1)  # Extract the video ID

    try:
        # Fetch transcript for the video ID
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine transcript text
        full_text = " ".join([entry['text'] for entry in transcript])

        # Placeholder for summarization logic
        summary = full_text[:500] + '...'  # Truncate for demonstration
        return summary
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Convert text to voice using gTTS
def text_to_speech(text):
    # Ensure the 'static/audio/' directory exists
    audio_folder = app.config['AUDIO_FOLDER']
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)
    
    # Create and save the audio file
    tts = gTTS(text)
    audio_path = os.path.join(audio_folder, 'output.mp3')
    tts.save(audio_path)
    
    return audio_path

# Convert voice to text using SpeechRecognition
def speech_to_text(audio_path):
    # Convert MP3 and other formats to WAV (if necessary)
    if not audio_path.endswith('.wav'):
        sound = AudioSegment.from_file(audio_path)
        audio_path_wav = audio_path.rsplit('.', 1)[0] + ".wav"
        sound.export(audio_path_wav, format="wav")
        audio_path = audio_path_wav  # Use the converted WAV file

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)  # Record the audio file
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Error connecting to the speech recognition service."

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/image-to-sketch', methods=['GET', 'POST'])
def image_to_sketch():
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                sketch_image_path = convert_to_sketch(file_path)
                return render_template('image_to_sketch.html', original_image=file_path, sketch_image=sketch_image_path)
    return render_template('image_to_sketch.html')

@app.route('/youtube-summarizer', methods=['GET', 'POST'])
def youtube_summarizer():
    if request.method == 'POST':
        if 'youtube_url' in request.form and request.form['youtube_url'].strip() != '':
            youtube_url = request.form['youtube_url']
            try:
                video_summary = summarize_youtube_video(youtube_url)
            except ValueError as e:
                video_summary = str(e)
            return render_template('youtube_summarizer.html', video_summary=video_summary)
    return render_template('youtube_summarizer.html')

@app.route('/text-to-voice', methods=['GET', 'POST'])
def text_to_voice():
    if request.method == 'POST':
        text = request.form['text']
        audio_path = text_to_speech(text)
        return send_file(audio_path, as_attachment=True)
    return render_template('text_to_voice.html')

@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text_route():
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
                filename = secure_filename(file.filename)
                audio_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
                file.save(audio_path)
                text = speech_to_text(audio_path)
                return render_template('speech_to_text.html', recognized_text=text)
    return render_template('speech_to_text.html')

if __name__ == '__main__':
    app.run(debug=True)
