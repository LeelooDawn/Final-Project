# Final-Project

CS50 Final Project

# Potluck Party!

#### Video Demo: The video is [linked here](https://youtu.be/axgyp2LX-QM)

**Potluck Party** is a simple website that helps you plan an event, put in how many dishes, and of what type, you need per event. This then sends an email to your invitees, lets them respond yes/no and tell you what dish they're bringing to the event.

This website relies heavily on databases. I want to be able to store all the information that creating an event requires. I also wanted to get better at Python and organizing everything while planning and building a website.

### Pages:

This Potluck Party has several pages:
**Profile Page:** This is the users profile page. It lets you see what events you've planned as well as the RSVPs coming in from your guests. This page will update as the people RSVP. The host can see which dish they have decided to bring

**Log In, Log Out, Register:** These are the simple Log In, Log Out, Register pages for the website.

**Dish Ideas:** This page allows any user to come in and search for recipe ideas. It will show you a picture of the recipe as well as a title and a simple link to the recipe.

**Plan Event:** This is the first page for people to plan events. It wants to know the Title of the Event, Event Theme, Event Location, and Event Date. This also asks what type of dishes does the Host need for this specific event.

**New Event:** This is the first confirmation page that the Host gets. It will show what the user wants and then allow them to put how many of each type of dish that they need. So maybe they only need some side-dishes and beverages, theyll be able to be specific on what they need.

**Confirm Event:** This is the second confirmation page, This allows the host to put in emails of the guests that they want to invite. It also shows exactly what they have put in for the invitees.

**Send Invitations:** This allows the user to send invitations.

**Email-Template:** The email sent to the user will take in the event details and have a button for the person to RSVP. It will take them to the RSVP page

**RSVP:** This page will have details for the event and ask the person if they can make the event or not.

**Yes:** If the user says yes, they will be brought to this page which will ask them what type of dish they are bringing as well as asking them to put in the text for the dish

**No:** If the user says no, this page will pop up saying "Sorry you can't make it" and asking them to register for the website and plan an event of their own.

**Error:** This page will tell people if they have any errors

### Cool Features:

The Host is able to see the event on their user profile page as well as updated RSVPS coming to the event and what dish they are bringing.

There is a separate "Dish Ideas" page which uses the Edamam API to search for recipe ideas. If they click on a recipe it will take them directly to the recipies website.

I designed the database myself which has:
USER Table - user_id, username, and hashed password
RSVP Table - rsvp_id, name, yes/no, linked to event_id
DISHES Table - dish text, name, the id of the type of dish, linked to rsvp_id
EVENTS table - event_name, event_date_time, event_location, event_theme, host_id (linked to user_id), event_id
DISHES_NEEDED table - dish_type (linked to dish_type table), amount_of_type, linked to event_id
DISH_TYPE table - dish_type_id, dish_type_text (i.e 1 = Entree, 2 = Side Dish, etc)

### Hiccups:

I am not able to get the Flask_Mail to work even tho I designed the separate HTML pages and functions to activate after someone sends mail. I think it might be because I need to "redirect" instead of "render_template" at some places, but I was not able to figure it out at this time. I did write the functions for the RSVPs.

### Ultimate Wishlist for this website:

I would love to have the website count down to the event date and send a reminder email to the invitees. The reminder email would remind them what dish they signed up to bring or send them to the dish-ideas page if they need help.
