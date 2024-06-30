from flask import Flask, request, render_template, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
import os
import shutil
import oracledb

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/pfp'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = 'supersecretkey'  # Replace with a real secret key

result = ''
loggedin_username = ''

# Uncomment to connect to database
conn = oracledb.connect(user="flaskserver", password="flask", dsn="localhost:1521/FREEPDB1")
cursor = conn.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
def change_profile_photo(username, new_photo_path=None):
    # Define the path to the user's profile photo directory
    user_dir = app.config['UPLOAD_FOLDER']
    
    # Ensure the user directory exists
    os.makedirs(user_dir, exist_ok=True)
    
    # Define the path to the profile photo
    profile_photo_name = f'{username}.jpg'
    profile_photo_path = os.path.join(user_dir, profile_photo_name)
    
    # Path to the default profile photo
    default_photo_path = os.path.join(user_dir, 'default_profile_photo.jpg')
    
    if new_photo_path:
        # If a new photo is provided, copy it to the user's profile photo directory
        shutil.copy(new_photo_path, profile_photo_path)
    else:
        # If no new photo is provided, use the default profile photo
        shutil.copy(default_photo_path, profile_photo_path)




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
    global loggedin_username
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cursor.execute(f"SELECT * FROM users where usr_name='{username}' AND usr_passwordhash='{password}'")
        result = cursor.fetchall()
        if len(result) == 0:
            return render_template("login.html", message="Invalid login credentials!")
        loggedin_username = username
        return redirect("/profile")
    
    return render_template("login.html", message=request.args.get('message'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    global loggedin_username
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        cursor.execute(f"SELECT * FROM users where usr_name='{username}' OR usr_email='{email}'")
        result = cursor.fetchall()
        if len(result) == 0:
            cursor.callproc('create_user', [username, email, password])
            conn.commit()
            loggedin_username = username
            return redirect("/profile")
        else:
            return render_template("signup.html", exists=True)
    
    return render_template("signup.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    global loggedin_username
    if loggedin_username == '':
        return redirect(url_for('.login', message="Please login!"))
    
    if request.method == "POST":
        if 'pfp' in request.files:
            file = request.files['pfp']
            if file.filename == '':
                flash('No selected file, setting default profile photo.')
                change_profile_photo(loggedin_username)
            elif file and allowed_file(file.filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{loggedin_username}.jpg')
                file.save(file_path)
                change_profile_photo(loggedin_username, file_path)
                flash('Profile photo successfully updated')
            else:
                flash('Invalid file type. Please upload an image.')
            return redirect(url_for('profile'))
    
    # Determine profile photo path
    profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{loggedin_username}.jpg')
    if not os.path.exists(profile_photo_path):
        profile_photo_path = url_for('static', filename='pfp/default_profile_photo.jpg')  # Default profile photo path
    
    return render_template("profile.html", username=loggedin_username, profile_photo=profile_photo_path)

@app.route("/plans")
def plans():
    return render_template("plans.html")

# @app.route("/convert", methods=["GET", "POST"])
# def convert():
#     if request.method == 'POST':
#         file = request.files['file']
#         fname = secure_filename(file.filename)
#         file.save('static/user_uploads/' + fname)
#         # do the processing here and save the new file in static/
#         fname_after_processing = 'user_uploads/' + fname
#         return jsonify({'result_image_location': url_for('static', filename=fname_after_processing)})
#     return render_template("convert.html")

if __name__ == '__main__':
    app.run(debug=True)
    app.secret_key = 'your_secret_key'
