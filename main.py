from word_detection import convert_to_text

from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
import re

import oracledb

app = Flask(__name__)
result = ''
loggedin_username = ''

# Uncomment to connect to database
conn = oracledb.connect(user="flaskserver", password="flask", dsn="localhost:1521/FREEPDB1")
cursor = conn.cursor()

@app.route("/")
def home():
    if not loggedin_username:
        return redirect("/convert")
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods =["GET", "POST"])
def login(message=None):
    global loggedin_username
    if request.method == "POST":
       # getting input with name = fname in HTML form
       username = request.form.get("username")
       password = request.form.get("password")
       cursor.execute(f"SELECT * FROM users where usr_name='{username}' AND usr_passwordhash='{password}'")
       result = cursor.fetchall()
       if len(result) == 0:
           return render_template("login.html", message="Invalid login credentials!")
       return redirect("/profile")
    
    return render_template("login.html", message=request.args.get('message'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    global loggedin_username
    if request.method == "POST":
        # Getting input from the form
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Check if username contains only allowed characters (alphanumeric and underscores)
        if not re.match(r'^\w+$', username):
            return render_template("signup.html", invalid_username=True)
        
        sql_query = f"SELECT * FROM users WHERE usr_name='{username}' OR usr_email='{email}'"
        cursor.execute(sql_query)
        result = cursor.fetchall()
        if len(result) == 0:
            cursor.callproc('create_user', [username, email, password])
            conn.commit()
            loggedin_username = username
            return redirect(url_for("profile"))  # Use url_for to dynamically get the profile route
        else:
            return render_template("signup.html", exists=True)

    return render_template("signup.html")


@app.route("/profile")
def profile():
    if loggedin_username=='':
        return redirect(url_for('.login', message="Please login!"))
        # return redirect("/login", message="Please login!")
    return render_template("profile.html", username=loggedin_username)

@app.route("/plans")
def plans():
    return render_template("plans.html")

@app.route("/convert", methods =["GET", "POST"])
def convert():
    if request.method == 'POST':
        file = request.files['file']
        fname = secure_filename(file.filename)
        file.save('static/user_uploads/' + fname)
        # do the processing here and save the new file in static/
        img_filename = 'user_uploads/'+fname
        output_text = convert_to_text('static/'+img_filename)
        return jsonify({'result_image_location': url_for('static', filename=img_filename),
                        'output_text': output_text})
    return render_template("convert.html")

@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

@app.route("/OTP")
def OTP():
    return render_template("OTP.html")
