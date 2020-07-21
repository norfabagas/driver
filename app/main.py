from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
import os
import requests
import json
import jwt

load_dotenv()

app = Flask(__name__)

@app.context_processor
def inject_app_information():
    return dict(
        app_name=os.getenv("APP_NAME")
    )

@app.route("/", methods=['GET'])
def home_view():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login_view():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        body = {
            'email': request.form['email'],
            'password': request.form['password']
            }

        jwt_key = requests.get(os.getenv("AUTH_GATE_URL") + "/api-secret", headers=headers)
        jwt_key = jwt_key.json()['data']

        response = requests.post(os.getenv("AUTH_GATE_URL") + "/login", headers=headers, json=body)        
        data = response.json()['data']

        decoded_jwt = jwt.decode(data['token'], jwt_key, algorithms=['HS256'])
        print(decoded_jwt)

        return jsonify({
            'data': data
        })
