# Lab_project_360
Lab project for a webpage with a database

Setup on your own:
This project was setup on python anywhere

make a Pythonanywhere account make a database in the database tab and choose a name for the Database like DiceShop

then use the Database schema.sql to create all the table then fill the items table with some dummy data so ther are some dice to show of you
can use our pictures in the pictures folder, important just put the path to the picture into the database.

After setting up the database the next thing is to set up the .env file in your Lab_project_360 folder like this
DB_USER="username"
DB_PASSWORD="password"
DB_HOST="username.mysql.pythonanywhere-services.com"
DB_NAME="username$databasename"
SECRET_KEY="anysecretkey"

after doing all that you will secure the flask_app.py put it some where else then go to the web tab and add a new webapp
which will create an empty flask_app.py in you folder Lab_project_360 then you simply delet that and past the saved one back in.

now in the webtab simply Configuration for username.pythonanywhere.com klick that link on top of the webpage and you webpage should open up
