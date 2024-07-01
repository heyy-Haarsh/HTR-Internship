from flask import Flask, request, render_template, redirect, url_for, jsonify, flash, session
from werkzeug.utils import secure_filename
import os
import errno
import shutil
from word_detection import convert_to_text
from image_processor import resize_img_square

import re
import oracledb

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/pfp'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = 'yarh-internship-secret'  # Replace with a real secret key

result = ''

conn = oracledb.connect(user="flaskserver", password="flask", dsn="localhost:1521/FREEPDB1")
cursor = conn.cursor()

default_pfp_path = app.config['UPLOAD_FOLDER']+'/default.jpg'

# This is to initialize session variables
@app.before_request
def initialize():
    if not session.get('logged_in'):
        session['logged_in'] = False
    if not session.get('username'):
        session['username'] = ''
    if not session.get('profile_photo_url'):
        session['profile_photo_url'] = default_pfp_path


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
def change_profile_photo(username, new_photo_path=None):
    # Define the path to the user's profile photo directory
    user_dir = app.config['UPLOAD_FOLDER']
    
    # Ensure the user directory exists
    os.makedirs(user_dir, exist_ok=True)
    
    # Define the path to the profile photo
    profile_photo_name = f'{username}.jpg'
    session['profile_photo_url'] = os.path.join(user_dir, profile_photo_name)
    
    # Path to the default profile photo
    default_photo_path = os.path.join(user_dir, 'default.jpg')
    
    if new_photo_path:
        # If a new photo is provided, copy it to the user's profile photo directory
        shutil.copy(new_photo_path, session['profile_photo_url'])
    else:
        # If no new photo is provided, use the default profile photo
        shutil.copy(default_photo_path, session['profile_photo_url'])




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login(message=None):
    if request.method == "POST":
        # getting input with name = fname in HTML form
        username = request.form.get("username")
        password = request.form.get("password")
        cursor.execute(f"SELECT * FROM users where usr_name='{username}' AND usr_passwordhash='{password}'")
        result = cursor.fetchall()
        if len(result) == 0:
           return render_template("login.html", message="Invalid login credentials!")
        session['logged_in'] = True
        session['username'] = username
        session['profile_photo_url'] = 'static/pfp/'+username
        return redirect("/profile")
    
    return render_template("login.html", message=message)

@app.route("/logout")
def logout():
    # Clear the session variables
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('profile_photo_url', None)
    return redirect('/')



@app.route("/logout")
def logout():
    global loggedin_username
    # Clear the session variables
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('profile_photo_url', None)
    loggedin_username = ''
    return redirect(url_for("home"))


@app.route("/signup", methods=["GET", "POST"])
def signup(message=None):
    if request.method == "POST":
        # Getting input from the form
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Check if username contains only allowed characters (alphanumeric and underscores)
        if not re.match(r'^\w+$', username):
            return render_template("signup.html", message="Username can only contain letters, numbers, and underscores!")
        if username=='default':
            return render_template("signup.html", message="Invalid username!")
        
        sql_query = f"SELECT * FROM users WHERE usr_name='{username}' OR usr_email='{email}'"
        cursor.execute(sql_query)
        result = cursor.fetchall()
        if len(result) == 0:
            cursor.callproc('create_user', [username, email, password])
            conn.commit()
            session['logged_in'] = True
            session['username'] = username
            session['profile_photo_url'] = 'static/pfp/'+username
            return redirect(url_for("profile"))  # Use url_for to dynamically get the profile route
        else:
            return render_template("signup.html", message="That username or email address is already taken!")

    return render_template("signup.html", message=message)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session['logged_in']:
        return redirect('/login', message="Please login!")
    
    if request.method == "POST":
        if 'pfp' in request.files:
            file = request.files['pfp']
            if file.filename == '':
                flash('No selected file, setting default profile photo.')
                session['profile_photo_url'] = default_pfp_path
                # change_profile_photo(session['username'])
            elif file and allowed_file(file.filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['username']}.jpg")
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.save(file_path)
                resize_img_square(file_path, 1000)
                session['profile_photo_url'] = file_path
                # change_profile_photo(session['username'], file_path)
                flash('Profile photo successfully updated')
            else:
                flash('Invalid file type. Please upload an image.')
            return redirect("/profile")
    
    # Determine profile photo path
    session['profile_photo_url'] = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['username']}.jpg")
    if not os.path.exists(session['profile_photo_url']):
        session['profile_photo_url'] = default_pfp_path  # Default profile photo path
    
    return render_template("profile.html")

@app.route("/plans")
def plans():
    return render_template("plans.html")

@app.route("/convert", methods =["GET", "POST"])
def convert():
    if not session['logged_in']:
        return redirect('/login')
    if request.method == 'POST':
        file = request.files['file']
        fname = secure_filename(file.filename)
        base_folder = 'user_uploads/'+session['username']
        folder = 'static/'+base_folder

        # Make the folder if it doesn't already exist
        try:
            os.makedirs(folder)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(folder):
                pass
            else: raise

        file.save(folder + '/' + fname)
        # do the processing here and save the new file in static/
        img_filename = base_folder + '/' + fname
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
