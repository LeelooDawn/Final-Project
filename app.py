import os

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)

#configure SQL database
db = "/users/leslienesbit/Documents/GitHub Projects/Final Project/potluck.db"
#make sure API key is set

#configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#app route index (profile page)
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
            return render_template("error.html", error="no username")
        elif not password:
            return render_template("error.html", error="no password") 
        #query database for username
        with sqlite3.connect(db) as con:
            cur = con.cursor()
            query = ("SELECT * FROM users WHERE username = ?", (username,))
            cur.execute(*query)
            user = cur.fetchone()
        
        return render_template("index.html", username=user[1])
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
        username = request.form.get("username"),
        password = request.form.get("password"),
        email = request.form.get("email") 
   
        #generate hash of password
        hash = generate_password_hash(password)
        add_user(username, hash, email)
        return render_template("index.html", username=username)
    else:
        return render_template("register.html")

        #enter new user into database
def add_user(username, hash, email):
    con = sqlite3.connect(db)
    cur = con.cursor()
    insert_user = ("INSERT INTO users (username, hash, email) VALUES (?,?,?)", (username, hash, email))
    cur.execute(insert_user)
    con.commit()
    con.close()
                #activate new session for user
                #new_user= cur.execute("SELECT id FROM users WHERE username = :username", username=username)
                #session["user_id"] = new_user[0]["id]
if __name__ == '__main__':
    app.run()  

