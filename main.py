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

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods =["GET", "POST"])
def login():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       username = request.form.get("username")
       return "Your name is "+username
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/plans")
def plans():
    return render_template("plans.html")

