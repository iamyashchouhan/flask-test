from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import edge_tts
import json
import random
import string
import os
import asyncio



app = Flask(__name__)

@app.route("/")
def start():
    return "The MBSA Server is Running"

# Function to generate a random filename
def generate_random_filename():
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(10))  # Generate a random string of length 10
    return f"{random_string}.wav"  # Add the file extension

# Function to save text to speech audio
async def text_to_speech_edge(text, language_code, voice="en-US-JennyNeural", rate="default", volume="default", pitch="default"):
    language_dict = {
        "English-Jenny (Female)": "en-US-JennyNeural",  # Add more language codes and corresponding voices if needed
    }
    voice = language_dict.get(language_code, voice)
    rate_value = rate if rate != "default" else "0%"  # Default rate value
    volume_value = volume if volume != "default" else "0%"  # Default volume value
    pitch_value = pitch if pitch != "default" else "0Hz"  # Default pitch value

    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=rate_value,  # Adjust rate (e.g., "-50%" for slower speech, "50%" for faster speech)
        volume=volume_value,  # Adjust volume (e.g., "-50%" for quieter speech, "50%" for louder speech)
        pitch=pitch_value,  # Adjust pitch (e.g., "-50Hz" for lower pitch, "50Hz" for higher pitch)
    )

    # Specify the desired file path in the root directory
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

    # Create the "audio" directory if it doesn't exist
    os.makedirs(audio_dir, exist_ok=True)

    # Generate a random filename
    random_filename = generate_random_filename()

    # Join the random filename with the audio directory path
    file_path = os.path.join(audio_dir, random_filename)

    await communicate.save(file_path)
    return file_path

with open("data.json", "r") as f:
    language_mappings = json.load(f)

@app.route("/languages", methods=["GET"])
def get_languages():
    return jsonify(language_mappings)

@app.route("/mbsa")
def mbsa():
    return render_template('index.html')

# Route to perform text-to-speech conversion
@app.route("/text-to-speech", methods=["POST", "GET"])
def text_to_speech():
    if request.method == "POST":
        data = request.get_json()
        text = data.get("text")
        language_code = data.get("language_code", "English-Jenny (Female)")
        voice = data.get("voice", "en-US-JennyNeural")  # Default to en-US-JennyNeural if not provided
        rate = data.get("rate", "0%")
        volume = data.get("volume", "0%")
        pitch = data.get("pitch", "0Hz")

        if text is None:
            return jsonify({"error": "Text parameter is required."}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output_audio_path = loop.run_until_complete(
            text_to_speech_edge(text, language_code, voice, rate, volume, pitch)
        )

        # Extract the filename from the output_audio_path
        filename = os.path.basename(output_audio_path)

        return jsonify({"audio_path": f"/audio/{filename}"})

    elif request.method == "GET":
        return "This endpoint only accepts POST requests.", 405

