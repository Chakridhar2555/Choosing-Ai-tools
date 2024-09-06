import os
import cv2
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Path to save uploaded images
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    video_id = video_url.split('v=')[-1]  # Extract YouTube video ID from the URL
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    full_text = " ".join([entry['text'] for entry in transcript])
    
    # Placeholder for summarization (you can use OpenAI to summarize)
    summary = full_text[:500] + '...'  # Truncate for demonstration
    return summary

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/image-to-sketch', methods=['GET', 'POST'])
def image_to_sketch():
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
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
            video_summary = summarize_youtube_video(youtube_url)
            return render_template('youtube_summarizer.html', video_summary=video_summary)
    return render_template('youtube_summarizer.html')


@app.route('/text-to-voice', methods=['GET', 'POST'])
def text_to_voice():
    # Add your text-to-voice functionality here
    return render_template('text_to_voice.html')


@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text():
    # Add your speech-to-text functionality here
    return render_template('speech_to_text.html')


if __name__ == '__main__':
    app.run(debug=True)
