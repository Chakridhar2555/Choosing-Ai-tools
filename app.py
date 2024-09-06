import os
import openai
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

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Generate AI image from text prompt using the latest OpenAI API
def generate_ai_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    return image_url

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

                # Convert to pencil sketch (existing feature)
                # sketch_image_path = convert_to_sketch(file_path)

                return render_template('index.html', original_image=file_path)

        elif 'prompt' in request.form and request.form['prompt'].strip() != '':
            # Handle AI image generation from text prompt
            prompt = request.form['prompt']
            ai_image_url = generate_ai_image(prompt)
            return render_template('index.html', ai_image=ai_image_url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
