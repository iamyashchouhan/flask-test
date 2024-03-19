from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import edge_tts
import json
import random
import string
import os
import asyncio
from gradio_client import Client
from bs4 import BeautifulSoup
import requests




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

@app.route('/get')
def scrape_and_render():
    # Fetch HTML content from the website
    url = 'https://temp-number.com/temporary-numbers/United-States/12085813709/1'
    response = requests.get(url)
    html_content = response.text

    # Render the HTML content in your Flask application
    return render_template('index.html', html_content=html_content)

@app.route("/country/<country>")
def get_country_data(country):
    try:
        url = f"https://temp-number.com/countries/{country}/1"
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Now you can use BeautifulSoup to extract data from the HTML content
        country_data = []
        country_boxes = soup.select("div.country-box")
        for box in country_boxes:
            time = box.select_one(".add_time-top").get_text().strip()
            phone_number = box.select_one(".card-title").get_text().strip()

            country_data.append({"time": time, "phoneNumber": phone_number, "country": country})

        return jsonify({"country": country, "countryData": country_data})

    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/tts", methods=["POST"])
def predict():
    try:
        # Get data from the POST request
        data = request.json

        # Extract input text and parameters from the data
        input_text = data.get("text", "")
        language_code = data.get("language_code", "English-Jenny (Female)")
        rate = int(data.get('rate', -10))
        volume = int(data.get('volume', -10))
        pitch = int(data.get('pitch', -10))

        # Initialize Gradio client
        client = Client("https://lelafav502-ttsstt.hf.space/")

        # Make prediction
        result = client.predict(
            input_text,
          language_code,
            rate,
            volume,
            pitch,
            api_name="/predict"
        )

        # Extract speech synthesis result and path
        text = result[0]
        path = result[1]

        # Create dictionary to hold response data
        response_data = {"text": text, "path": path}

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})

