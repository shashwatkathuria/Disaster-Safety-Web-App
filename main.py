import os
import datetime

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash


import sqlite3

conn = sqlite3.connect('alerts.db')
db = conn.cursor()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/commonalerts", methods=["GET", "POST"])

def commonalerts():

    if request.method == "POST":
        if not request.form.get("calamity"):
            return "Must enter the calamity."
        elif not request.form.get("location"):
            return "Must enter the location"

        c = request.form.get("calamity")
        l = request.form.get("location")
        d = request.form.get("description")
        s = {"success":"yes"}
        db.execute("INSERT INTO commonalerts (calamity,location,description) VALUES (?,?,?)",
                       (c,l,d))
        conn.commit()
        return jsonify(s)
    else:
        return render_template("alerts.html")

@app.route("/getcommonalerts")

def getcommonalerts():

    alerts=[]
    w = db.execute("SELECT * FROM commonalerts ORDER BY id DESC ")
    for w1 in w:
        s = {"datetime":w1[1],"location":w1[3],"calamity":w1[2],"description":w1[4]}
        alerts.append(s)

    return jsonify(alerts)

@app.route("/govtalerts", methods=["GET", "POST"])

def govtalerts():

    if request.method == "POST":
        if not request.form.get("username"):
            return "Must enter a username"
        elif not request.form.get("password"):
            return "Must enter the password"
        elif not request.form.get("calamity"):
            return "Must enter the calamity"
        elif not request.form.get("location"):
            return "Must enter the location"
        elif not request.form.get("description"):
            return "Must enter the description"

        username=request.form.get("username")
        password=request.form.get("password")
        rows = db.execute("SELECT * FROM govtids WHERE username = ?",(username,))
        row = db.fetchone()
        if row is None or not check_password_hash(row[2], request.form.get("password")):
            return "Invalid username and/or password"


        c = request.form.get("calamity")
        l = request.form.get("location")
        d = request.form.get("description")
        s = {"success":"yes"}

        db.execute("INSERT INTO govtalerts (calamity,location,description) VALUES (?,?,?)",
                       (c,l,d))
        conn.commit()
        return jsonify(s)
    else:
        return render_template("govtalerts.html")

@app.route("/getgovtalerts")

def getgovtalerts():

    alerts=[]
    w = db.execute("SELECT * FROM govtalerts ORDER BY id DESC ")
    for w1 in w:
        s = {"datetime":w1[1],"location":w1[3],"calamity":w1[2],"description":w1[4]}
        alerts.append(s)
    return jsonify(alerts)

@app.route("/generateids")

def generateids():
    usernames=["earthquakeagencyofindia","hurricaneagencyofindia","floodagencyofindia","disastermanagementagencyofindia"]
    passwords=["eaoi","haoi","faoi","dmaoi"]

    for i in range(4):
        db.execute("INSERT INTO govtids (username,password) VALUES (?,?)",(usernames[i],generate_password_hash(passwords[i])))

@app.route("/viewgovtalerts")

def viewgovtalerts():

    alerts=[]
    w = db.execute("SELECT * FROM govtalerts ORDER BY id DESC ")
    for w1 in w:
        s = {"datetime":w1[1],"location":w1[3],"calamity":w1[2],"description":w1[4]}
        alerts.append(s)
    return render_template("view.html",rows=alerts,alert="GOVT. ISSUED ALERTS")

@app.route("/viewcommonalerts")

def viewcommonalerts():

    alerts=[]
    w = db.execute("SELECT * FROM commonalerts ORDER BY id DESC ")
    for w1 in w:
        s = {"datetime":w1[1],"location":w1[3],"calamity":w1[2],"description":w1[4]}
        alerts.append(s)
    return render_template("view.html",rows=alerts,alert="COMMON ALERTS")

if __name__ == '__main__':
  app.run()
