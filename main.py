from flask import Flask, request, render_template

#import oracledb

app = Flask(__name__)

myname = "Bob"

result = ''

# Uncomment to connect to database
#conn = oracledb.connect(user="flaskserver", password="flask", dsn="localhost:1521/FREEPDB1")

@app.route("/")
def home():
    return render_template("index.html", name=myname)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/plans")
def plans():
    return render_template("plans.html")

