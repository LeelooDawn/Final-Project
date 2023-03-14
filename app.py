import os

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3 as db


app = Flask(__name__)

#configure SQlite database
db = sqlite3.connect("potluck.db")

#make sure API key is set

#configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#app route index (profile page) @login-required
@app.route("/")
def index():
    if not session.get("username"):
        return redirect("login.html")
    return render_template("index.html")
 
 #app route login user 
@app.route("/login", methods=["POST", "GET"])
def login():

    #forget any user_id
    session.clear()

    #if form is submitted via post
    if request.method == "POST":
        if not request.form.get("username"):
            return ("Must Provide Username")
        elif not request.form.get("password"):
            return ("Must Provide Password") 
        #query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "Invalid username and/or password"

        session["user_id"] = rows[0]["id"]   

        return redirect("index.html")
    else:
    return render_template("login.html")


#app route logout user
@app.route("/logout")
def logout():
    #forget any user_id
	session.clear()
    #redirect user to log in form
	return redirect("login.html")

#app route register user 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        #validate if username, password, email are not blank
        if not name:
            return "Please enter a username"
        elif not password:
            return "Please enter a password"
        elif not email:
            return "Please enter your email" 

        #generate hash of password
        hash = generate_password_hash(password)
        #if username is taken return apology
        if db.execute("SELECT username FROM users WHERE username = :name", username=name):
            return "Username already exists"
        #enter new user into database
        db.execute("INSERT INTO users (name, hash) VALUES (?,?)", name, hash)
        #activate new session for user
        new_user= db.execute("SELECT id FROM users WHERE username = :name", username=name)
        session["user_id"] = new_user[0]["id"]
        #redirect to login page
        return redirect("/login")
        #else via GET redirect to register page
    else:
        return render_template("register.html")

