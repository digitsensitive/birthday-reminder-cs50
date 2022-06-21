from database import MySQL
import datetime
from flask import Flask, redirect, render_template, request, session
from flask_mail import Mail, Message
from flask_session import Session
from helpers import get_month_name, login_required
import os
from scheduler import BirthdayReminderScheduler
from werkzeug.security import check_password_hash, generate_password_hash
import sys

# Init Flask instance
app = Flask(__name__)

# Loop through mapping object of process environment
# https://docs.python.org/3/library/os.html#os.environ
for key, value in os.environ.items():
    # Get the keys with the prefix BR_, which stands for
    # the app name (Birthday reminder) and set it in the app config
    if key.startswith("BR_"):
        env_name = key.split("BR_")[1]
        app.config[env_name] = value

# Init Mail instance
mail = Mail(app)

# Init Session
Session(app)

# Create a connection and cursor object to represent the database
mysql = MySQL(app)
connection = mysql.get_connection("birthday_reminder")


def send_mail():

    # Create cursor
    cursor = connection.cursor(buffered=True)

    # Get all birthdays where email notification is enabled
    query = "SELECT * FROM birthdays WHERE email_notification = 1"
    cursor.execute(query)
    birthdays = cursor.fetchall()

    # Close cursor
    cursor.close()

    # Get the current date
    today = datetime.date.today()

    # Loop through birthdays
    for birthday in birthdays:

        current_age = 0
        next_birth_date = datetime.date(
            today.year, birthday[3].month, birthday[3].day)

        reminder_days = datetime.timedelta(7)

        # Evaluate for current year if the birthday has passed or not
        if today <= next_birth_date:
            # For the current year the birthday is upcoming
            current_age = today.year - birthday[3].year
        elif today > next_birth_date:
            # For the current year the birthday has passed already
            next_birth_date = datetime.date(
                today.year+1, birthday[3].month, birthday[3].day)
            current_age = today.year - birthday[3].year+1

        if today+reminder_days == next_birth_date:
            # App Context:
            # https://stackoverflow.com/questions/40117324/querying-model-in-flask-apscheduler-job-raises-app-context-runtimeerror
            with app.app_context():
                msg = Message(subject=app.config.get("MAIL_SUBJECT"),
                              sender=app.config.get("MAIL_USERNAME"),
                              recipients=["caviezelkuhn@gmail.com"],
                              body=birthday[2] + " will turn " + str(current_age) + " in 7 days!")
                mail.send(msg)


# Add a BackgroundScheduler with Advanced Python Scheduler
# Event is triggered every 24 hours
# https://apscheduler.readthedocs.io
scheduler = BirthdayReminderScheduler(True)
scheduler.add_job(send_mail, 24)


@app.route("/")
@login_required
def index():
    # Create cursor
    cursor = connection.cursor(buffered=True)

    # Get birthdays where display on main page is True and limit to 5 entries
    query = ("SELECT * FROM birthdays WHERE display_on_main_page = 1 LIMIT 5")
    cursor.execute(query)
    birthdays = cursor.fetchall()

    # Close cursor
    cursor.close()

    # Get the current date for calculation of days until birthday
    today = datetime.date.today()

    # Create empty birthday array
    birthdays_array = []

    # Loop through selected birthdays
    for birthday in birthdays:

        # Set variables
        days_until_birthday = 0
        current_age = 0
        percentage_until_birthday = 0

        # Calculate date of the next birthday
        next_birth_date = datetime.date(
            today.year, birthday[3].month, birthday[3].day)

        # Evaluate for current year if the birthday has passed or not
        if today <= next_birth_date:
            # For the current year the birthday is upcoming
            current_age = today.year - birthday[3].year
        elif today > next_birth_date:
            # For the current year the birthday has passed already
            next_birth_date = datetime.date(
                today.year+1, birthday[3].month, birthday[3].day)
            current_age = today.year - birthday[3].year+1

        days_until_birthday = (next_birth_date - today).days
        percentage_until_birthday = 100-0.274*days_until_birthday

        birthdays_array.append({'name': birthday[2],
                                'birth_date': birthday[3],
                                'gender': birthday[4],
                                'age': current_age,
                                'days_until_birthday': days_until_birthday,
                                'percentage': percentage_until_birthday})

    birthdays_array.sort(key=lambda x: x['days_until_birthday'])
    return render_template("index.html", birthdays=birthdays_array)


@app.route("/add-birthday", methods=["GET", "POST"])
@login_required
def add_birthday():
    if request.method == "POST":

        # Create cursor
        cursor = connection.cursor(buffered=True)

        # Get the form data
        first_name = request.form.get("firstName")
        birth_date = request.form.get("birthDate")
        gender = request.form['genderSelection']
        display_on_main_page = 'displayOnMainPage' in request.form
        email_notification = 'automaticEmailNotification' in request.form

        # Check if a first name was entered
        if not first_name:
            return render_template("add-birthday.html", error_message="Missing first name. ")

        # Check if a birthday was entered
        if not birth_date:
            return render_template("add-birthday.html", error_message="Missing birthday. ")

        # Add birthday to database
        new_birthday = (
            "INSERT INTO birthdays (user_id, name, birth_date, gender, display_on_main_page, email_notification) VALUES(%s, %s, %s, %s, %s, %s)")
        data = (session["user_id"],
                first_name,
                birth_date,
                gender,
                display_on_main_page,
                email_notification)
        cursor.execute(new_birthday, data)
        connection.commit()

        # Close cursor
        cursor.close()

        return redirect("/")

    return render_template("add-birthday.html")


@app.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):

    # Create cursor
    cursor = connection.cursor(buffered=True)

    if request.method == "POST":

        # Get the form data
        first_name = request.form.get("firstName")
        birth_date = request.form.get("birthDate")
        gender = request.form['genderSelection']
        display_on_main_page = 'displayOnMainPage' in request.form
        email_notification = 'automaticEmailNotification' in request.form

        # Check if a first name was entered
        if not first_name:
            return render_template("edit-birthday.html", error_message="Missing first name. ")

        # Check if a birthday was entered
        if not birth_date:
            return render_template("edit-birthday.html", error_message="Missing birthday. ")

        # Add birthday to database
        new_birthday = (
            "UPDATE birthdays SET name = %s, birth_date = %s, gender = %s, display_on_main_page = %s, email_notification = %s WHERE id = %s")
        data = (first_name,
                birth_date,
                gender,
                display_on_main_page,
                email_notification,
                id)
        cursor.execute(new_birthday, data)
        connection.commit()

        return redirect("/list-birthdays")

    if request.method == "GET":
        query = ("SELECT * FROM birthdays WHERE id = %s")
        cursor.execute(query, (id,))
        birthday = cursor.fetchone()

        birthday_dict = {'id': birthday[0],
                         'name': birthday[2],
                         'birth_date': birthday[3],
                         'gender': birthday[4],
                         'display_on_main_page': birthday[5],
                         'email_notification': birthday[6]}

        return render_template('edit-birthday.html', birthday=birthday_dict)

    # Close cursor
    cursor.close()


@app.route('/delete/<int:id>', methods=["GET"])
@login_required
def delete(id):
    # Create cursor
    cursor = connection.cursor(buffered=True)

    query = ("DELETE FROM birthdays WHERE id = %s")
    cursor.execute(query, (id,))
    connection.commit()

    # Close cursor
    cursor.close()

    return redirect('/list-birthdays')


@app.route("/list-birthdays", methods=["GET"])
@login_required
def list_birthdays():

    # Create cursor
    cursor = connection.cursor(buffered=True)

    # Create empty array for birthdays
    birthdays_sorted_by_month = []

    # Loop through the 12 months (1, 2, 3, ..., 12)
    for i in range(1, 13):
        # Create empty array for birthdays of the current month
        birthdays = []

        # Get all the birthdays in the selected month and sort the birthday
        # by the day (from early to late)
        query = (
            "SELECT * FROM birthdays WHERE MONTH(birth_date) = %s ORDER BY DAY(birth_date) ASC")
        cursor.execute(query, (i,))
        birthdays_of_selected_month = cursor.fetchall()

        # Convert month int to full month name
        full_month_name = get_month_name(str(i))

        # Add month string to the dictionary
        birthdays.append({'month': full_month_name})

        # Loop over birthdays of the current month
        for birthday in birthdays_of_selected_month:
            # Append dictionary to array with id, name, birth date and month
            birthdays.append({'id': birthday[0],
                              'name': birthday[2],
                              'birth_date': birthday[3],
                              'month': full_month_name})

        # Add birthdays array to the birthdays array sorted by month
        birthdays_sorted_by_month.append(birthdays)

    # Close cursor
    cursor.close()

    return render_template("list-birthdays.html", birthdays_per_month=birthdays_sorted_by_month)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":

        # Create cursor
        cursor = connection.cursor(buffered=True)

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
        query = "SELECT * FROM users WHERE username = %s"
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

        # Close cursor
        cursor.close()

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Create cursor
        cursor = connection.cursor(buffered=True)

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
        user = "INSERT INTO users (username, hash) VALUES(%s, %s)"
        data = (username, generate_password_hash(password))
        cursor.execute(user, data)
        connection.commit()

        # Close cursor
        cursor.close()

        return redirect("/")
    return render_template("register.html")


if __name__ == "__main__":
    # https://flask.palletsprojects.com/en/2.1.x/api/#application-object
    # Host:
    # Set to '0.0.0.0' makes the server available externally as well.
    # Debug:
    # Set to True so the server will automatically reload for code changes
    app.run(host='0.0.0.0', debug=True)
