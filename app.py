import os

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)

#make sure API key is set

#configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#app route index (profile page) @login-required
@app.route("/")
def index():
#show profile of user

#check if user has any events coming up - if not say "no events coming up - plan something here!"
#api of recipes will show up at bottom
   return render_template("index.html")
 
 #app route login user 
@app.route("/login", methods=["GET", "POST"])
def login():
    #if form is submitted via post
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return ("Must Provide Username")
        elif not password:
            return ("Must Provide Password") 
        #query database for username
        with sqlite3.connect("/users/leslienesbit/Documents/GitHub Projects/Final Project/potluck.db") as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            rows = con.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = rows.fetchone()[0]
        
        return render_template("/")
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
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            email = request.form.get("email")
            if not username:
                return "Please enter username"
            elif not password:
                return "Please enter password"
            elif not email:
                return "Please enter email"
        #generate hash of password
            hash = generate_password_hash(password)
    
        #enter new user into database
            with sqlite3.connect("/users/leslienesbit/Documents/GitHub Projects/Final Project/potluck.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, hash, email) VALUES (?,?,?)", (username, hash, email))
        #activate new session for user
                con.commit()
                message = "User successfully added"
                #activate new session for user
                #new_user= cur.execute("SELECT id FROM users WHERE username = :username", username=username)
                #session["user_id"] = new_user[0]["id"]
        except:
            con.rollback()
        #redirect to index page
        finally:
            return redirect("/login")
            con.close()
        #else via GET redirect to register page
    else:
        return render_template("register.html")

