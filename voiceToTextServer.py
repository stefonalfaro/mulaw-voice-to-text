import json
from flask import Flask, abort, request, jsonify
import sys
import threading
import queue
from transformers import pipeline  # Ensure this is correctly imported
import torch
import torchaudio  # Import torch for tensor operations
from transformers import Wav2Vec2Processor, Wav2Vec2Model

def load_config():
    try:
        with open('config/config.json', 'r') as config_file:
            config = json.load(config_file)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error loading configuration file.")
        sys.exit(1)

print("Start PP AI EAVA Voice to Text Server.")

app_config = load_config()
api_key = app_config.get('apikey')
modelName = app_config.get('modelName')

app = Flask(__name__)
processor = Wav2Vec2Processor.from_pretrained(modelName)
model = Wav2Vec2Model.from_pretrained(modelName)

asr_pipeline = pipeline("automatic-speech-recognition", model=modelName)

task_queue = queue.Queue()
print("Model loaded.")

def task_processor():
    with app.app_context():
        while True:
            task = task_queue.get()
            pcm_data, response_queue = task
            try:
                waveform = torch.tensor([pcm_data]).float() / 32768.0  # Normalize if needed

                # Resample your audio to 16kHz using torchaudio or similar if necessary, assuming your audio needs resampling from 8kHz to 16kHz
                if waveform.shape[1] / 8000 > 1:  # Simple check to decide if resampling might be needed
                    resampler = torchaudio.transforms.Resample(orig_freq=8000, new_freq=16000)
                    waveform = resampler(waveform)

                # Convert the waveform tensor to the format expected by the pipeline, the pipeline expects a numpy array, not a PyTorch tensor
                audio_numpy = waveform.squeeze().numpy()

                # Use the pipeline for speech recognition
                result = asr_pipeline(audio_numpy)
                text = result['text']  # Extract the text from the result
                
                response_queue.put(jsonify(text))
            except Exception as e:
                response_queue.put(jsonify({"error": str(e)}))

threading.Thread(target=task_processor, daemon=True).start()

def validate_token():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(" ")[1]
        if token == api_key:
            return True
    return False

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if not validate_token():
            print("[401] Unauthorized Access Attempt")
            abort(401)

        if 'pcm_data' not in request.json:
            print("[400] Invalid request format.")
            abort(400, description="Invalid request format.")

        pcm_data = request.json['pcm_data']
        
        response_queue = queue.Queue()
        task_queue.put((pcm_data, response_queue))
        response = response_queue.get()
        return response
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)