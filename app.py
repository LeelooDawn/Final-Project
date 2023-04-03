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
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=5)
app.config["SECRET_KEY"] = config.SECRET_KEY
sess = Session()
sess.init.app(app)

#app route index (profile page)
@app.route("/")
def index():
#show profile of user
    if "username" in session:
        username = session["username"]
            return render_template("index.html")    
#check if user has any events coming up - if not say "no events coming up - plan something here!"
#api of recipes will show up at bottom
    else: 
        return render_template("login.html")
   
 
 #app route login user 
@app.route("/login", methods=["GET", "POST"])
def login():
    #forget any user
    session.pop("username", None)
    #if form is submitted via post
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error="Please enter username/password"
        if not username:
            return render_template("error.html", error=error)
        elif not password:
            return render_template("error.html", error=error) 
        #query database for username
        with sqlite3.connect(db) as con:
            cur = con.cursor()
            query = ("SELECT * FROM users WHERE username = ?", (username,))
            cur.execute(*query)
            user = cur.fetchone()
        #if user is in database, start a session for user
        if user:
            session["loggedin"] = True
            session["id"]= user[0]
            session["username"] = user[1]
            return render_template("index.html", username=user[1])
        #else it is incorrect and try again
        else:
            err="Incorrect username/password"
            return render_template("error.html", error=err)
    elif request.method == "GET":
        return render_template("login.html")


#app route logout user
@app.route("/logout")
def logout():
    #forget any user_id
	session.pop("username", None)
    #redirect user to log in form
	return redirect("login.html")

#app route register user 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username"),
            password = request.form.get("password"),
            email = request.form.get("email") 
            error = "Please enter your registration information again"
            if not username:
                return render_template("error.html", error=error)
            elif not password:
                return render_template("error.html", error=error)
            elif '@' not in email:
                return render_template("error.html", error=error) 
        #generate hash of password
            hash = generate_password_hash(password)
        #enter new user into database
            with sqlite3.connect(db) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, hash, email) VALUES (?,?,?)", (username, hash, email))
                con.commit()
                new_user = cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                new_user = cur.fetchone()
            #start new session for user
            if new_user:
                session["loggedin"] = True
                session["id"]= new_user[0]
                session["username"] = new_user[1]
        except:
            err = "Error registering user, please try again"
            return render_template("error.html", error=err)
        finally:
            return render_template("index.html", username=session["username"])
            con.close()
    elif request.method == "GET":
        return render_template("register.html")

                
                #new_user= cur.execute("SELECT id FROM users WHERE username = :username", username=username)
                #session["user_id"] = new_user[0]["id]
if __name__ == '__main__':
    app.run()  

