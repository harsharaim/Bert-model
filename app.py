from flask import Flask, request, jsonify
import os
import moviepy.editor as mp
import speech_recognition as sr
import logging
from flask_cors import CORS
from transformers import BertForSequenceClassification, BertTokenizer
from torch.utils.data import DataLoader, TensorDataset
import torch

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

# Load the BERT model and tokenizer


model_path = '/home/prax/Desktop/finalYearProject/cyber_model-20240426T134555Z-001/cyber_model'
model = BertForSequenceClassification.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

def predict_user_input(input_text, model, tokenizer, device):
    user_input = [input_text]

    user_encodings = tokenizer(user_input, truncation=True, padding=True, return_tensors="pt")
    user_dataset = TensorDataset(user_encodings['input_ids'], user_encodings['attention_mask'])
    user_loader = DataLoader(user_dataset, batch_size=1, shuffle=False)

    model.eval()
    with torch.no_grad():
        for batch in user_loader:
            input_ids, attention_mask = [t.to(device) for t in batch]
            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predictions = torch.sigmoid(logits)

    predicted_labels = (predictions.cpu().numpy() > 0.5).astype(int)
    labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

    # Filter labels without a predicted value of 1
    result = [label for i, label in enumerate(labels) if predicted_labels[0][i] == 1]
    return result

@app.route('/', methods=['GET'])
def home():
    return jsonify({'api': "root"})

@app.route('/transcribe_video', methods=['POST'])
def transcribe_video():
    # Check if the 'video' file is present in the request
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'})

    video_file = request.files['video']

    # Check if the file name is empty
    if video_file.filename == '':
        return jsonify({'error': 'No selected video file'})

    # Ensure 'uploads' directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    video_path = os.path.join("uploads", video_file.filename)
    video_file.save(video_path)

    # Process the video to transcribe audio to text
    input_string = process_video_audio(video_path)

    # Return the transcription as response
    return jsonify({'transcription': input_string})

@app.route('/compute', methods=["POST"])
def compute():
    # Get the transcribed text from the request
    if 'transcription' not in request.json:
        return jsonify({'error': 'No transcription provided'})

    input_text = request.json['transcription']

    # Predict using the text classification model
    predicted_labels = predict_user_input(input_text, model, tokenizer, device)

    return jsonify({'predicted_labels': predicted_labels})

def process_video_audio(video_path):
    video = mp.VideoFileClip(video_path)
    
    # Extract audio from the video
    audio = video.audio

    temp_audio_file = "temp.wav"
    success = audio.write_audiofile(temp_audio_file, codec='pcm_s16le', fps=44100)

    if success:
        print(f"Audio file successfully written to: {temp_audio_file}")
    else:
        print("Failed to write audio file")

    recognizer = sr.Recognizer()
    audio_duration = audio.duration
    print(f"Audio duration: {audio_duration} seconds")

    chunk_duration = 10 
    input_string = ''

    for i in range(int(audio_duration / chunk_duration)):
        start_time = i * chunk_duration
        end_time = (i + 1) * chunk_duration

        with sr.AudioFile(temp_audio_file) as source:
            audio_data = recognizer.record(source, duration=chunk_duration, offset=start_time)

            try:
                text = recognizer.recognize_google(audio_data)
                input_string = input_string + ' ' + text
                print(f"Text from chunk {i + 1}: {text}")
            except sr.UnknownValueError:
                print(f"Google Web Speech API could not understand audio in chunk {i + 1}")
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API in chunk {i + 1}; {e}")

    print(input_string)
    audio.close()
    
    # Close the video file
    video.close()
    # Remove temporary audio file
    os.remove(temp_audio_file)

    return input_string


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
