import os
import cv2
# import openai  # Uncomment this when you want to use OpenAI's API
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Path to save uploaded images
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Uncomment and set your OpenAI API Key if using OpenAI's API
# openai.api_key = os.getenv("OPENAI_API_KEY")

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

# Temporary fix: Generate placeholder image URL instead of making API call
def generate_ai_image_temp(prompt):
    # Temporary placeholder image
    return "https://via.placeholder.com/512?text=AI+Generated+Image"

# ChatGPT/OpenAI Feature: Generate AI image from text prompt (commented out for now)
# def generate_ai_image_openai(prompt):
#     response = openai.Image.create(
#         prompt=prompt,
#         n=1,
#         size="512x512"
#     )
#     image_url = response['data'][0]['url']
#     return image_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            # Handle file upload for pencil sketch
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Convert to pencil sketch
                sketch_image_path = convert_to_sketch(file_path)

                return render_template('index.html', original_image=file_path, sketch_image=sketch_image_path)

        elif 'prompt' in request.form and request.form['prompt'].strip() != '':
            # Handle AI image generation from text prompt (Temporary Fix)
            prompt = request.form['prompt']
            ai_image_url = generate_ai_image_temp(prompt)

            # Uncomment this if using OpenAI's API
            # ai_image_url = generate_ai_image_openai(prompt)
            
            return render_template('index.html', ai_image=ai_image_url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
