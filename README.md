# Final-Project

CS50 Final Project

# Potluck Party!

#### Video Demo: <URL HERE>

#### Description- Your README.md file should be minimally multiple paragraphs in length, and should explain what your project is, what each of the files you wrote for the project contains and does, and if you debated certain design choices, explaining why you made them. Ensure you allocate sufficient time and energy to writing a README.md that documents your project thoroughly. Be proud of it! If it is too short, the system will reject it.:

The Potluck Party is a simple website that helps you plan an event, tell how many dishes and of what type you need per event. This then sends an email to your invitees, lets them respond yes/no and tell you what dish they're bringing to the event.

This website relies heavily on databases.

Cool Features:
The Host is able to see the event on their user profile page as well as updated RSVPS coming to the event and what dish they are bringing.

    There is a separate "Dish Ideas" page which uses the Edamam API to search for recipe ideas. If they click on a recipe it will take them directly to the recipies website.

    I Built the database myself which has:
        USER Table - user_id, username, and hashed password
        RSVP Table - rsvp_id, name, yes/no, linked to event_id
        DISHES Table - dish text, name, the id of the type of dish, linked to rsvp_id
        EVENTS table - event_name, event_date_time, event_location, event_theme, host_id (linked to user_id), event_id
        DISHES_NEEDED table - dish_type (linked to dish_type table), amount_of_type, linked to event_id
        DISH_TYPE table - dish_type_id, dish_type_text (i.e 1 = Entree, 2 = Side Dish, etc)

Ultimate Wishlist for this website: I would love to have the website count down to the event date and send a reminder email to the invitees. The reminder email would remind them what dish they signed up to bring.
