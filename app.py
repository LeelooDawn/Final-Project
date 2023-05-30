import os

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from py_edamam import Edamam
import sqlite3
from functools import wraps
from datetime import datetime

app = Flask(__name__)

#configure SQL database
db = "/users/leslienesbit/Documents/GitHub Projects/Final Project/potluck.db"

#Log-in Required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
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
       #JOIN rsvp ids of rsvp table/dishes table that are associated with event id that user is a host of
       #- yes/no, name, dish text, dish type

    return render_template("index.html")    



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
    if request.method == "POST":
        #get all information from form
        event_title = request.form.get("eventtitle")
        event_theme = request.form.get("eventtheme")
        datetime = request.form.get("datetime")
        event_location = request.form.get("eventlocation")
        selected_dishes = request.form.getlist("selection")
        #make sure no fields are left blank
        error = "All fields are required"
        if not event_title and event_theme and datetime and event_location and selected_dishes:
            return render_template ("error.html", error=error)

        convert_datetime = datetime.strptime(datetime, "%Y-%m-%dT%H:%M")
        formatted_datetime= convert_datetime.strftime("%B %-d %Y, %-I:%M %p")

        return render_template("/events/newevent.html", name=event_title, theme=event_theme, datetime=datetime, location=event_location, selected_dishes=selected_dishes)
    else:
        return render_template("events.html")    

#APP ROUTE - CONFIRM EVENT INFORMATION
@app.route("/events/newevent", methods=["GET", "POST"])
@login_required
def newevent():
    #get host id
    host_id = session.get("id")
    #create connection to database
    con = sqlite3.connect(db)
    cur = con.cursor()
    #establish variables for dish_type
    entree_type = 1
    side_dish_type = 2
    dessert_type = 3
    beverage_type = 4
    dish_ware_type = 5

    if request.method == "POST":
        event_title = request.form.get("name")
        datetime = request.form.get("datetime")
        event_theme=request.form.get("theme")
        event_location=request.form.get("location")
        entree_amount = request.form.get("entrees")
        side_dish_amount = request.form.get("side_dish")
        dessert_amount = request.form.get("desserts")
        beverage_amount = request.form.get("beverages")
        dish_ware_amount = request.form.get("dish_ware")
        #create a dishes_needed tuple to pair the dish type with the amount
        dishes_needed = []
        if entree_amount:
            dishes_needed.append((entree_type, entree_amount))
        if side_dish_amount:
            dishes_needed.append((side_dish_type, side_dish_amount))
        if dessert_amount:
            dishes_needed.append((dessert_type, dessert_amount))
        if beverage_amount:
            dishes_needed.append((beverage_type, beverage_amount))
        if dish_ware_amount:
            dishes_needed.append((dish_ware_type, dish_ware_amount))
        #begin adding event to database
        cur.execute("BEGIN")
        #add event time, location, title
        new_event = cur.execute("INSERT INTO events (event_name, event_date_time, event_location, event_theme, host_id) VALUES (?,?,?,?,?)", (event_title, datetime, event_location, event_theme, host_id))
        #get created event primary id
        event_id = cur.lastrowid
        #enter dishes information
        event_dishes_needed = cur.executemany("INSERT INTO dishes_needed (dish_type, amount_of_type, event_id) VALUES(?,?,?)", [(*dish, event_id) for dish in dishes_needed])
        #commit all transactions
        cur.execute("COMMIT")
        cur.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
        event_data = cur.fetchall()
        con.close()

        #convert number to text within my list of tuples (ex: (1 ,4) into (entree, 4))
        number_to_text = {
            1 : "Entree",
            2 : "Side Dish",
            3 : "Dessert",
            4 : "Beverage",
            5 : "Dishware"
        }
        convert_dishes_needed = [(number_to_text[num], second_num) for num, second_num in dishes_needed]
        #render template with event data and dishes amount
        return render_template("events/confirm.html", event_data=event_data, dishes_needed=convert_dishes_needed)
    else:
        return render_template("events/newevent.html")

@app.route("/events/confirm", methods=["GET", "POST"])
def confirm()

#enter emails and names into a form to send out
#Send Grid email format
#send emails with all information

#in email the person should be able to hit yes or no

#app_route("/events/event-id/RSVP")
#def RSVP
#if method is post - #get answer from RSVP email ("YES" or "NO")
    #if RSVP is no
    #enter answer & name into RSVP database
    #show "Sorry you can't make it, create your own event here"
    #if RSVP is yes
    #enter answer & Name into RSVP database
    #ask attendee to put in name, text of dish they're bringing, what type of dish
        #the type will be written out like 1-entree, 2-sidedish, etc
    #enter information into dishes database


@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    #contact API 
    user_id = session.get("id")

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

