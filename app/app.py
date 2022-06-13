from database import MySQL
import datetime
from flask import Flask, redirect, render_template, request, session
from flask_mail import Mail, Message
from flask_session import Session
from helpers import login_required, split_date
import os
from scheduler import BirthdayReminderScheduler
from werkzeug.security import check_password_hash, generate_password_hash

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
cursor = connection.cursor(buffered=True)


def send_mail():
    # query = ("SELECT * FROM birthdays")

    # cursor.execute(query)
    # birthdays_of_selected_month = cursor.fetchall()

    # App Context:
    # https://stackoverflow.com/questions/40117324/querying-model-in-flask-apscheduler-job-raises-app-context-runtimeerror
    with app.app_context():
        msg = Message(subject="Geburtstagserinnerung",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=["caviezelkuhn@gmail.com"],
                      body="This is a test email I sent with Gmail and Python!")
        mail.send(msg)


# Add a BackgroundScheduler with Advanced Python Scheduler
# Event is triggered every 24 hours
# https://apscheduler.readthedocs.io
scheduler = BirthdayReminderScheduler(True)
scheduler.add_job(send_mail, 24)


@app.route("/")
@login_required
def index():
    # Query
    query = ("SELECT * FROM birthdays WHERE display_on_main_page=1 LIMIT 5")
    cursor.execute(query)
    birthdays = cursor.fetchall()

    # Get the current date for calculation of days until birthday
    today = datetime.date.today()

    # Create array
    birthdays_dict = []
    for b in birthdays:

        birth_date = datetime.date(today.year, b[3].month, b[3].day)
        days_until_birthday = 0
        age = 0
        if today <= birth_date:
            birth_date = datetime.date(today.year, b[3].month, b[3].day)
            days_until_birthday = birth_date - today
            age = today.year - b[3].year
        elif today > birth_date:
            birth_date = datetime.date(today.year+1, b[3].month, b[3].day)
            days_until_birthday = birth_date - today
            age = today.year - b[3].year+1

        birthdays_dict.append({'name': b[2],
                               'birth_date': b[3],
                               'gender': b[4],
                               'day': b[3].day,
                               'month': b[3].month,
                               'year': b[3].year,
                               'age': age,
                               'days_until_birthday': days_until_birthday.days,
                               'percentage': 100-0.274*days_until_birthday.days})

    birthdays_dict.sort(key=lambda x: x['days_until_birthday'])
    return render_template("index.html", birthdays=birthdays_dict)


@app.route("/add-birthday", methods=["GET", "POST"])
@login_required
def add_birthday():
    if request.method == "POST":

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

        split_birth_date = split_date(birth_date)

        # Add birthday to database
        new_birthday = (
            "INSERT INTO birthdays (user_id, name, birth_date, gender, day, month, year, display_on_main_page, email_notification) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)")
        data = (session["user_id"],
                first_name,
                birth_date,
                gender,
                split_birth_date['day'],
                split_birth_date['month'],
                split_birth_date['year'],
                display_on_main_page,
                email_notification)
        cursor.execute(new_birthday, data)
        connection.commit()

        return redirect("/")

    return render_template("add-birthday.html")


@app.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
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

        split_birth_date = split_date(birth_date)

        # Add birthday to database
        new_birthday = (
            "UPDATE birthdays SET name = %s, birth_date = %s, gender = %s, day = %s, month = %s, year = %s, display_on_main_page = %s, email_notification = %s WHERE id = %s")
        data = (first_name,
                birth_date,
                gender,
                split_birth_date['day'],
                split_birth_date['month'],
                split_birth_date['year'],
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
                         'display_on_main_page': birthday[8],
                         'email_notification': birthday[9]}

        return render_template('edit-birthday.html', birthday=birthday_dict)


@app.route('/delete/<int:id>', methods=["GET"])
@login_required
def delete(id):

    if request.method == "GET":
        query = ("DELETE FROM birthdays WHERE id = %s")
        cursor.execute(query, (id,))
        connection.commit()
        return redirect('/list-birthdays')


@app.route("/list-birthdays", methods=["GET"])
@login_required
def list_birthdays():

    birthdays_sorted_by_month = []
    # Querys
    for i in range(1, 13):
        query = ("SELECT * FROM birthdays WHERE month = %s ORDER BY month ASC")

        cursor.execute(query, (i,))
        birthdays_of_selected_month = cursor.fetchall()

        birthdays_dict = []

        datetime_object = datetime.datetime.strptime(str(i), "%m")
        full_month_name = datetime_object.strftime("%B")
        birthdays_dict.append({'current_month': full_month_name})
        for b in birthdays_of_selected_month:
            datetime_object = datetime.datetime.strptime(str(b[6]), "%m")
            full_month_name = datetime_object.strftime("%B")
            birthdays_dict.append({'id': b[0],
                                   'name': b[2],
                                   'birth_date': b[3],
                                   'day': b[5],
                                   'month': full_month_name})
        birthdays_sorted_by_month.append(birthdays_dict)

    return render_template("list-birthdays.html", birthdays_per_month=birthdays_sorted_by_month)


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
@login_required
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
