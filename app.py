import os

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from py_edamam import Edamam
import sqlite3
from functools import wraps

app = Flask(__name__)

#configure SQL database
db = "/users/leslienesbit/Documents/GitHub Projects/Final Project/potluck.db"

#Log-in Required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if sesson.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#make sure API key is set in server start


#configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#app route index (profile page)
@app.route("/")
@login_required
def index():
#show profile of user
    username = session.get("username")
       
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
@app.route("/events", methods=["GET", "POST"])
@login_required
def events():
# USER CREATES EVENT BY ENTERING INFORMATION INTO EVENT TABLE
    host_id = session.get("user_id")

    if request.method == "POST":
        event_title = request.form.get("eventtitle")
        event_theme = request.form.get("eventtheme")
        datetime = request.form.get("datetime")
        event_location = request.form.get("eventlocation")
        #make sure no fields are left black
        error = "All fields are required"
        if not all(event_title, event_theme, datetime, event_location):
            return render_template ("error.html", error=error)
        #add event to database
        with sqlite3.connect(db) as con:
            cur = con.cursor() 
            data = cur.execute("INSERT INTO events (event_name, event_date_time, event_location, event_theme, host_id) VALUES (?,?,?,?,?)", (event_title, datetime, event_location, event_theme, host_id))
            con.commit()
        #user chooses how many dishes needed for event
        #show new event in new_event html

        return render_template("event.html", dishes=dishes)
    else:
        return render_template("event.html", dishes=dishes )

#APP ROUTE - CONFIRM EVENT INFORMATION & SEND INVITATIONS

@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    #contact API 
    user_id = session.get("user_id")

    recipe = Edamam(
        recipes_appid=os.environ.get('APP_ID'),
        recipes_appkey=os.environ.get('APP_KEY'),
    )
#if request method POST
    if request.method == "POST":
        try:
            #get search text from user
            search = request.form.get("search")
            hits = recipe.search_recipe(search)['hits']
            recipe_list = []
            for hit in hits:
                r = hit['recipe']
                label = r['label']
                source = r['source']
                url = r['url']
                image = r['image']
                recipe_list.append({'recipe': r, 'label': label, 'image':image, 'source': source, 'url':url})
            return render_template("recipes.html", recipe_list=recipe_list)
        except Exception as e:
            err = f"Error in search: {e}"
            return render_template("error.html", error=err)
        
    else: 
        return render_template("recipes.html")
        
        
if __name__ == '__main__':
    app.run()  

