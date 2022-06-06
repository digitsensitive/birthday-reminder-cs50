from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from database import MySQL
import datetime

import sys
# print(row, file=sys.stderr)

# Create a Flash instance
app = Flask(__name__)

# Create a connection and cursor object to represent the database
mysql = MySQL(app)
connection = mysql.get_connection("birthday_reminder")
cursor = connection.cursor(buffered=True)

# Configure Sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():

    # Query
    query = ("SELECT * FROM birthdays LIMIT 3")
    cursor.execute(query)
    birthdays = cursor.fetchall()

    # Get the current date for calculation of days until birthday
    today = datetime.date.today()

    # Create array
    birthdays_dict = []
    for b in birthdays:

        birth_date = datetime.date(today.year, b[3].month, b[3].day)
        days_until_birthday = 0
        if today <= birth_date:
            birth_date = datetime.date(today.year, b[3].month, b[3].day)
            days_until_birthday = birth_date - today
        elif today > birth_date:
            birth_date = datetime.date(today.year+1, b[3].month, b[3].day)
            days_until_birthday = birth_date - today

       # print(days_until_birthday, file=sys.stderr)

        birthdays_dict.append({'name': b[2],
                               'birth_date': b[3], 'days_until_birthday': days_until_birthday.days})

    birthdays_dict.sort(key=lambda x: x['days_until_birthday'])
    return render_template("index.html", birthdays=birthdays_dict)


@app.route("/add-birthday", methods=["GET", "POST"])
def add_birthday():
    if request.method == "POST":

        # Get the form data
        first_name = request.form.get("first-name")
        birth_date = request.form.get("birth_date")

        # Check if a first name was entered
        if not first_name:
            return render_template("add-birthday.html", error_message="Missing first name. ")

        # Check if a birthday was entered
        if not birth_date:
            return render_template("add-birthday.html", error_message="Missing birthday. ")

        # Add birthday to database
        new_birthday = (
            "INSERT INTO birthdays (user_id, name, birth_date) VALUES(%s, %s, %s)")
        data = (session["user_id"], first_name, birth_date)
        cursor.execute(new_birthday, data)
        connection.commit()

        return redirect("/")

    return render_template("add-birthday.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":

        # Get the form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if a username was entered
        if not username:
            return render_template("login.html", error_message="Missing username. ")

        # Check if a password was entered
        if not password:
            return render_template("login.html", error_message="Missing password. ")

        # Query database for username
        query = "SELECT * FROM users WHERE username=%s"
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        # Ensure if username exists
        if row is None:
            return render_template("login.html", error_message="Invalid username. ")

        # Ensure username or password is correct
        if not check_password_hash(row[2], password):
            return render_template("login.html", error_message="Invalid username and/or password. ")

        # Remember which user has logged in
        session["user_id"] = row[0]

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Get the form data
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")

        # Check if a username was entered
        if not username:
            return render_template("register.html", error_message="Missing username. ")

        # Evaluate if the user does already exist
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        if row:
            return render_template("register.html", error_message="Username already exists. ")

        # Check if a password was entered
        if not password:
            return render_template("register.html", error_message="Missing password. ")

        # Check if a password confirmation was entered
        if not password_confirmation:
            return render_template("register.html", error_message="Missing password confirmation. ")

        # Check if password and password confirmation are equal
        if password != password_confirmation:
            return render_template("register.html", error_message="Passwords do not match. ")

        # Add user to database
        user = ("INSERT INTO users (username, hash) VALUES(%s, %s)")
        data = (username, generate_password_hash(password))
        cursor.execute(user, data)
        connection.commit()

        return redirect("/")
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
