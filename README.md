# Final-Project

CS50 Final Project

# Potluck Party!

#### Video Demo: The video is [linked here]()

**Potluck Party** is a simple website that helps you plan an event, put in how many dishes, and of what type, you need per event. This then sends an email to your invitees, lets them respond yes/no and tell you what dish they're bringing to the event.

This website relies heavily on databases. I want to be able to store all the information that creating an event requires. I also wanted to get better at Python and organizing everything while planning and building a website.

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
