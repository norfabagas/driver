from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.context_processor
def inject_app_information():
    return dict(app_name=os.getenv("APP_NAME"))

@app.route("/", methods=['GET'])
def home_view():
    return render_template("home.html")