# session
Creating a Flask server with sessions.
This Flask-based server uses a postgresQL database that has various movies and coffee shops in several cities.
The DB also has three users with passwords and zipcodes.
When you run the server, you can search witout logging in to see all of the data that matches.
You can also login and the searches will filter based on the zip code of the user.
Users can logout.
Since the server uses Flask session variables, multiple users can use the site.
You can also create a new account from the login page.
When you create a new account, the password is encrypted with Blowfish before being added to the DB.
