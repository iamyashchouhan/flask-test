from flask import Flask, render_template, request, jsonify, send_from_directory
import json


app = Flask(__name__)

@app.route("/")
def start():
    return "The MBSA Server is Running"

with open("data.json", "r") as f:
    language_mappings = json.load(f)

@app.route("/languages", methods=["GET"])
def get_languages():
    return jsonify(language_mappings)

@app.route("/mbsa")
def mbsa():
    return render_template('index.html')

