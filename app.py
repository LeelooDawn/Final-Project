import os

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from py_edamam import Edamam
import sqlite3
from functools import wraps
from datetime import datetime
from flask_mail import Mail, Message, get_body
from blinker import signal

app = Flask(__name__)
app.config['MAIL_SERVER']= 'localhost' 
app.config['MAIL_PORT'] = 25
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_SUPPRESS_SEND'] = True
mail = Mail(app)



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
    user_id = session.get("id")

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("BEGIN")
    cur.execute("SELECT event_id FROM events WHERE host_id = ?", (user_id,))
    event_ids = cur.fetchall()
   
    event_data=[]

    for event_id in event_ids:
        query = cur.execute("SELECT event_name, event_date_time, event_theme, event_location, rsvp.name, rsvp.response, dishes.dish FROM events JOIN rsvp ON rsvp.event_id = events.event_id JOIN dishes ON dishes.rsvp_id = rsvp.rsvp_id WHERE events.event_id = ?", (event_id[0],))
        fetched_data = cur.fetchall()
        event_data.extend(fetched_data)
            #convert date time
        for row in fetched_data:
            event_date_time = datetime.strptime(row[1], "%Y-%m-%dT%H:%M")
            formatted_datetime= event_date_time.strftime("%B %-d %Y, %-I:%M %p")
            row = row[:1] + (formatted_datetime,) + row[2:]
            event_data.append(row)

    
    con.close()
    return render_template("index.html", event_data=event_data)    



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
        date_time = request.form.get("datetime")
        event_theme=request.form.get("theme")
        event_location=request.form.get("location")
        entree_amount = request.form.get("entrees")
        side_dish_amount = request.form.get("side_dish")
        dessert_amount = request.form.get("desserts")
        beverage_amount = request.form.get("beverages")
        dish_ware_amount = request.form.get("dish_ware")

        #check if event exists already
        cur.execute("SELECT event_id FROM events WHERE event_name = ? AND event_date_time = ? AND event_location = ? AND host_id = ?", (event_title, date_time, event_location, host_id),)
        existing_event=cur.fetchone()
        if existing_event:
            con.close()
            err = "This event exists already!"
            return render_template ("error.html", error=err)
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
        new_event = cur.execute("INSERT INTO events (event_name, event_date_time, event_location, event_theme, host_id) VALUES (?,?,?,?,?)", (event_title, date_time, event_location, event_theme, host_id))
        #get created event primary id
        event_id = cur.lastrowid
        #enter dishes information
        event_dishes_needed = cur.executemany("INSERT INTO dishes_needed (dish_type, amount_of_type, event_id) VALUES(?,?,?)", [(*dish, event_id) for dish in dishes_needed])
        #commit all transactions
        cur.execute("COMMIT")
        cur.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
        event_data = cur.fetchall()
        con.close()
        #convert time into user friendly text
        date_new = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        formatted_datetime= date_new.strftime("%B %-d %Y, %-I:%M %p")
        #convert number to text within my list of tuples (ex: (1 ,4) into (entree, 4))
        number_to_text = {
            1 : "Entree",
            2 : "Side Dish",
            3 : "Dessert",
            4 : "Beverage",
            5 : "Dishware"
        }
        convert_dishes_needed = [(number_to_text[num], second_num) for num, second_num in dishes_needed]
        #get event_id and store in session variables
        event_id = event_data[0][0]
        session['event_data'] = event_data
        session['event_id'] = event_id
        session['formatted_datetime'] = formatted_datetime
        #render template with event data and dishes amount
        return render_template("events/confirm.html", event_data=event_data, event_id=event_id, formatted_datetime=formatted_datetime, dishes_needed=convert_dishes_needed)
    else:
        return render_template("events/newevent.html")

@app.route("/events/<int:event_id>/confirm", methods=["GET", "POST"])
def confirm(event_id):
    event_id = event_id
    username = session.get("username")
    host_id = session.get("id")
    event_data = session.get("event_data")
    formatted_datetime=session.get("formatted_datetime")

    subject = "You're Invited to a Potluck Party!"

#enter emails and names into a form to send out
    if request.method == "POST":
        names = request.form.getlist("name")
        emails = request.form.getlist("email")
        recipients = []
        for name, email in zip(names, emails):
            recipients.append(email)
        send_email(recipients, subject, names)
    else:
        return render_template("events/confirm.html")
#send email function
    def send_email(recipients, subject, names):
        for name, email in zip(names, recipients):
        msg = Message(subject, recipients=[email])
        msg.html = render_template("email_template.html", name=name, event_data=event_data, event_id=event_id, formatted_datetime=formatted_datetime, username=username)
        mail.send(msg)
    return "Invites sent successfully!"

#if RSVP is yes
def will_attend(event_id):
event_id = event_id
con = sqlite3.connect(db)
cur = con.cursor()
    #get dish data from event-data to show how many dishes the person needs

cur.execute("SELECT dish_type, amount_of_type FROM dishes WHERE event_id = ?", (event_id,))
dish_data = cur.fetchall()
dish_list = []
for dish_type, amount_of_type in dish_data:
    if dish_type == 1:
        dish_text = "Entree"
    if dish_type == 2:
        dish_text == "Side Dish"
    if dish_type == 3:
        dish_text == "Desserts"
    if dish_type == 4:
        dish_text == "Beverages"
    if dish_type == 5:
        dish_text == "Dish Ware"

    dish_info = f"{dish_text} = {amount_of_type}"
    dish_list.append(dish_info)
#ask attendee to put in name, text of dish they're bringing, what type of dish 
    if request.method == "POST"
        name = request.form.get("name")
        response = request.form.get("response")
        dishtext = request.form.get("dishtext")
        dishtype = request.form.get("dishtype")

        response = True 
        cur.execute=("BEGIN")
        #insert the RSVP response
        cur.execute=("INSERT INTO rsvps (event_id, name, response) VALUES (?, ?, ?)", (event_id, name, response))
        rsvp_id = cur.lastrowid
        #insert the dishes response
        cur.execute=("INSERT INTO dishes(dishtext, name, dishtype, rsvp_id) VALUES(?,?,?,?)", (dishtext, name, dishtype, rsvp_id))
        cur.execute=("COMMIT")
        con.close()

        return "You've successfully RSVPd, See you Soon!"
return render_template("/rsvps/rsvp/yes.html", dishes=dish_list)
          
@app.route("/rsvps/rsvp/<int:event_id>")
def rsvp(event_id):
    event_id = event_id
    email = request.get_json()
    body = email["content"]
    name = get_name_from_email(body)
    con = sqlite3.connect(db)
    cur = con.cursor()

    if request.method == "POST":
        response = request.form.get("response")
    #if RSVP is no
        if response == "no":
            no = False 
            cur.execute = ("INSERT INTO rsvps (event_id, name, response) VALUES (?, ?, ?)", (event_id, name, no))
            cur.close()
            con.close()
            return render_template("rsvps/no.html")
        if response == "yes":
            will_attend(event_id)
            return redirect("rsvps/yes.html")
    else:
        return render_template("/rsvps/rsvp/<int:event_id>")


return render_template("rsvps/rsvp.html")
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

