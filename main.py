from flask import Flask, request, render_template

#import oracledb

app = Flask(__name__)
result = ''

# Uncomment to connect to database
#conn = oracledb.connect(user="flaskserver", password="flask", dsn="localhost:1521/FREEPDB1")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

<<<<<<< HEAD
=======
@app.route("/contact")
def contact():
    return render_template("contact.html")

>>>>>>> ff153b6ae066cbdc30da5bd81f34af7239b16cb1
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

<<<<<<< HEAD
@app.route("/plans")
def plans():
    return render_template("plans.html")

=======
>>>>>>> ff153b6ae066cbdc30da5bd81f34af7239b16cb1
