import os
import uuid
import base64
import subprocess
import sys
from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
from transcriber import transcribe_audio
from summarizer import summarize_text

app = Flask(__name__, static_folder='public', static_url_path='/')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB upload limit

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_AUDIO_EXT = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.webm'}

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    model_size = request.form.get('model', 'base')
    
    if not audio_file.filename:
        return jsonify({'error': 'Empty filename'}), 400
        
    ext = os.path.splitext(audio_file.filename)[1].lower()
    if ext not in ALLOWED_AUDIO_EXT:
        return jsonify({'error': f'Unsupported file type: {ext}'}), 400
        
    original_filename = secure_filename(audio_file.filename) or 'audio.raw'
    filename = f"{uuid.uuid4().hex}_{original_filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    audio_file.save(filepath)
    
    try:
        result = transcribe_audio(filepath, model_size)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        result = summarize_text(
            text=data['text'],
            original_lang=data.get('language', 'en'),
            target_lang=data.get('target_lang', 'en')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_pdf', methods=['POST'])
def save_pdf():
    data = request.json
    if not data or 'pdf_base64' not in data:
        return jsonify({'error': 'No pdf data provided'}), 400
        
    pdf_base64 = data['pdf_base64']
    filename = data.get('filename', 'Meeting_Minutes.pdf')
    
    if "base64," in pdf_base64:
        pdf_base64 = pdf_base64.split("base64,")[1]
        
    try:
        pdf_bytes = base64.b64decode(pdf_base64)
        filepath = os.path.join(os.getcwd(), filename)
        
        if os.path.exists(filepath):
            base, ext = os.path.splitext(filename)
            filepath = os.path.join(os.getcwd(), f"{base}_{uuid.uuid4().hex[:6]}{ext}")
            
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        
        try:
            if os.name == 'nt':
                os.startfile(filepath)
            elif sys.platform == 'darwin':
                subprocess.call(('open', filepath))
            else:
                subprocess.call(('xdg-open', filepath))
        except Exception as open_err:
            print("Could not auto-open file:", open_err)
            
        return jsonify({'message': f'Successfully saved and opened {filepath}'})
    except Exception as e:
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)
