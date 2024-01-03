from flask import Flask, render_template, request, jsonify
import os
import moviepy.editor as mp
import speech_recognition as sr
import logging

app = Flask(__name__,static_folder='static')
app.logger.setLevel(logging.DEBUG)

@app.route('/', methods=['GET'])
def homePage():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
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

    input_string = process_video_audio(video_path)
    return jsonify({'text': input_string})

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
