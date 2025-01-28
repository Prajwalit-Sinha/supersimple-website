from flask import Flask, render_template, request
from PIL import Image
import pytesseract
from langdetect import detect
import os

app = Flask(__name__)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Create uploads folder if not exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Language detection function
def detect_language(text):
    try:
        lang = detect(text)
    except:
        lang = 'unknown'  # Default to unknown if detection fails
    return lang

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = ''
    autocorrected_text = ''
    detected_lang = ''
    uploaded_message = ''
    filename = ''

    if request.method == 'POST':
        # Check if the user uploaded a file
        if 'image' not in request.files:
            return render_template('index.html', message="No file part")
        
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', message="No selected file")

        # If the file is allowed, save it
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            uploaded_message = "File uploaded successfully"

            # Get the selected language
            selected_lang = request.form.get('language_select', 'eng')  # Default to English

            # Language mapping for pytesseract
            lang_mapping = {
                'eng': 'eng',
                'hin': 'hin',
                'mix': 'eng+hin'
            }
            tesseract_lang = lang_mapping.get(selected_lang, 'eng')

            # Process the image using pytesseract
            img = Image.open(filename)
            extracted_text = pytesseract.image_to_string(img, lang=tesseract_lang)

            # Autocorrect the extracted text (basic example)
            autocorrected_text = extracted_text.replace('nme', 'name').replace('teh', 'the')  # Add more corrections here

            # Detect the language of the extracted text
            detected_lang = detect_language(extracted_text)

            return render_template('index.html',
                                   uploaded_message=uploaded_message,
                                   extracted_text=extracted_text,
                                   autocorrected_text=autocorrected_text,
                                   detected_lang=detected_lang,
                                   selected_lang=selected_lang)

    return render_template('index.html', uploaded_message=uploaded_message)

if __name__ == '__main__':
    app.run(debug=True)
