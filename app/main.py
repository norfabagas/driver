from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response, flash
from werkzeug.wrappers import Request
from dotenv import load_dotenv
import os, requests, json, jwt
from .middleware import Middleware
import app.modules.token as token
from app.modules.session import *
from app.modules.globals import *

# Booted up before flask app
load_dotenv()

app = Flask(__name__, instance_relative_config=False)

# Initialize
app.wsgi_app = Middleware(app.wsgi_app)
app.secret_key = os.getenv("SECRET_KEY")

@app.context_processor
def inject_app_information():
    return dict(
        app_name=os.getenv("APP_NAME")
    )

@app.before_request
def before_request():
    url = request.url
    method = request.method
    root = request.url_root
    
    excluded_path = [
        root + 'login',
        root + 'register'
    ]

    if (url in excluded_path) or ("static/" in url):
        return
    else:
        auth_cookie = request.cookies.get('auth')
        if auth_cookie != None:
            if is_session_valid(auth_cookie):
                return
            else:
                flash('You need to login first', 'info')
                return redirect(url_for('login_view'))
        else:
            flash('You need to login first', 'info')
            return redirect(url_for('login_view'))

@app.route("/", methods=['GET', 'POST'])
def home_view():
    if request.method == 'GET':
        return render_template("home.html")
    if request.method == 'POST':
        text = request.form['text']
        category = "NN"
        lowered = text.lower()
        if "internet" in lowered:
            category = "INTERNET"
        elif "tv" in lowered:
            category = "IPTV"
        elif "voice" in lowered:
            category = "VOICE"
        
        return render_template("home.html", category=category)

@app.route("/login", methods=['GET', 'POST'])
def login_view():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        # Retrieve token secret
        status_code, jwt_key = token.get_token_secret()

        if status_code != 200:
            return render_template("500.html", message="Error fetching token")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        body = {
            'email': request.form['email'],
            'password': request.form['password']
        }

        response = requests.post(os.getenv("AUTH_SERVICE_URL") + "/v1/login", headers=headers, json=body)
        if response.status_code == 200:
            data = response.json()['data']

            decoded_jwt = token.decode_token(data['token'])
            
            generate_auth_session(
                decoded_jwt['authorized'],
                decoded_jwt['exp'],
                decoded_jwt['user_id'],
                data['name'],
                data['email'],
                data['token']
            )

            resp = make_response(
                redirect(url_for("home_view"))
            )

            resp.set_cookie("auth", decoded_jwt['user_id'])

            return resp
        else:
            data = response.json()['data']
            flash(data['error'], "danger")
            return render_template(
                "login.html",
                email=request.form['email']
            )

@app.route('/logout', methods=["GET"])
def logout():
    user_id = request.cookies.get("auth")
    if user_id:
        session.pop(user_id)
        resp = make_response(
            redirect(url_for("login_view"))
        )
        resp.set_cookie("auth", "", expires=0)
        
        return resp
    else:
        return

@app.route('/register', methods=["GET", "POST"])
def register_view():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        body = {
            "name": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"]
        }

        if "" in body.values():
            print("meow")
            flash("Please fill out all field", "danger")
            return render_template(
                "register.html",
                name=request.form["name"],
                email=request.form["email"]
            )

        if not is_duplicate(request.form['password'], request.form['password_confirmation']):
            flash("Password and Password Confirmation does not match", "danger")

            return render_template(
                "register.html",
                name=request.form["name"],
                email=request.form["email"]
            )

        response = requests.post(os.getenv("AUTH_SERVICE_URL") + "/v1/register", headers=get_request_header(), json=body)
        if response.status_code == 201:
            flash("Register successful! Now Log on with your account", "success")

            return redirect(url_for("login_view"))
        else:
            data = response.json()['data']
            flash(data['error'], "danger")

            return render_template(
                "register.html",
                name=request.form["name"],
                email=request.form["email"]
            )
    else:
        return render_template("500.html", message="Prohibited")

@app.route("/profile", methods=['GET'])
def profile_view():
    headers = {
        'Authorization': 'Bearer ' + session.get(request.cookies.get('auth'))['token']
    }
    response = requests.get(os.getenv("AUTH_SERVICE_URL") + "/v1/user", headers=headers)
    if response.status_code == 200:
        data = response.json()['data']

        return render_template("profile.html", data=data)
    else:
        return render_template("500.html", message="Error on fetching data")