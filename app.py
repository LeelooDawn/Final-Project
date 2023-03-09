import os

from flask import Flask, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3 as db


app = Flask(__name__)

#configure SQlite database

#make sure API key is set

#configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#app route index (profile page) @login-required
@app.route("/")
def index():
    if not session.get("username"):
        return redirect("login")
    return render_template('index.html')
 
 #app route login user 
@app.route("/login", methods=["POST", "GET"])
def login():
    #if form is submitted
    if request.method == "POST":
        session["username"] = request.form.get("username")
        return redirect("/")
    return render_template("login.html")


#app route logout user
@app.route("/logout")
def logout():
	session["username"] = None
	return redirect("/")

#app route register user 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        #validate if username, password, email are not blank
        #generate hash of password
        #if username is taken return apology
        #enter new user into database
        #activate new session for user
        #redirect to login page
        #else via GET redirect to register page

