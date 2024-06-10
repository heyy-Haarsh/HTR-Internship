from flask import Flask
from flask import render_template
from flask import request

import oracledb

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