import os

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import sqlite3

app = Flask(__name__)

#configure SQL database
db = "/users/leslienesbit/Documents/GitHub Projects/Final Project/potluck.db"

#make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")

#configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#app route index (profile page)
@app.route("/")
def index():
#show profile of user
    if not session.get("username"):
        return redirect("/login")
       
    return render_template("index.html")    
#check if user has any events coming up - if not say "no events coming up - plan something here!"
#api of recipes will show up at bottom


 #app route login user 
@app.route("/login", methods=["GET", "POST"])
def login():
    #forget any user
    session.pop("username", None)
    #if form is submitted via post
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        #if there are blanks in either form show error
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
	return redirect("/")

#app route register user 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            email = request.form.get("email") 
            #if any field is blank show error
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
                #now select the user you just entered as new_user
                new_user = cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
                new_user = cur.fetchone()

            #start new session for user
                if new_user:
                    session["loggedin"] = True
                    session["id"]= new_user[0]
                    session["username"] = new_user[1]
                    return render_template("index.html", username=new_user[1])
                    con.close()
        except Exception as e:
            err = f"Error registering user: {e}"
            return render_template("error.html", error=err)     
    elif request.method == "GET":
        return render_template("register.html")

#app route create event
@app.route("/event", methods=["GET", "POST"])
def event():
#insert event date, time, theme/title into database
#choose how many different dishes they need for the event using a @dish_amounts function
#render a html that has the confirmation information as well as space to enter emails to send to friends
#confirm and send emails

#dish_amounts function
   
    return render_template("event.html")

@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    #contact API 
    if request.method == "POST":
        search = request.form.get("search")
        url = "https://tasty.p.rapidapi.com/recipes/auto-complete"

        querystring = {"prefix": search}

        headers = {
	        "X-RapidAPI-Key": "f66876ee1emshc8619abd70c59f0p150fbejsne5d7073b1edc",
	        "X-RapidAPI-Host": "tasty.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)  
        #parse response
        response.raise_for_status()
        results = []
        for item in response.json()["results"]:
            display = item["display"]
            ingredient = item["type"]
            search_value = item["search_value"]
            results.append({"display" : display, "type": ingredient, "search_value":search_value})

        return render_template("recipes.html", results=results)
    else:
        url = "https://tasty.p.rapidapi.com/recipes/auto-complete"

        querystring = {"prefix":"chicken soup"}

        headers = {
	        "X-RapidAPI-Key": "f66876ee1emshc8619abd70c59f0p150fbejsne5d7073b1edc",
	        "X-RapidAPI-Host": "tasty.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response.raise_for_status()
        results = []
        for item in response.json()["results"]:
            display = item["display"]
            ingredient = item["type"]
            search_value = item["search_value"]
            results.append({"display" : display, "type": ingredient, "search_value":search_value})

        return render_template("recipes.html", results=results)
        
        
if __name__ == '__main__':
    app.run()  

