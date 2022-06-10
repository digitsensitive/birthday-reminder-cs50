from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import split_date
from database import MySQL
import datetime
from flask_mail import Mail, Message

# import sys
# print(row, file=sys.stderr)

# Create a Flash instance
app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "auto.birthday.reminder@gmail.com",
    "MAIL_PASSWORD": "ikwrymusouahvuhi"
}

app.config.update(mail_settings)

# Mail
mail = Mail(app)

# Create a connection and cursor object to represent the database
mysql = MySQL(app)
connection = mysql.get_connection("birthday_reminder")
cursor = connection.cursor(buffered=True)

# Configure Sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


Session(app)


def job():
   # query = ("SELECT * FROM birthdays")

    # cursor.execute(query)
    # birthdays_of_selected_month = cursor.fetchall()

    # App Context:
    # https://stackoverflow.com/questions/40117324/querying-model-in-flask-apscheduler-job-raises-app-context-runtimeerror
    with app.app_context():
        msg = Message(subject="Hello",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=["caviezelkuhn@gmail.com"],
                      body="This is a test email I sent with Gmail and Python!")
        mail.send(msg)


scheduler = BackgroundScheduler()
scheduler.start()
# job = scheduler.add_job(job, 'interval', seconds=5)


@app.route("/")
def index():

    # Query
    query = ("SELECT * FROM birthdays WHERE display_on_main_page=1 LIMIT 3")
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

        birthdays_dict.append({'name': b[2],
                               'birth_date': b[3],
                               'days_until_birthday': days_until_birthday.days})

    birthdays_dict.sort(key=lambda x: x['days_until_birthday'])
    return render_template("index.html", birthdays=birthdays_dict)


@app.route("/add-birthday", methods=["GET", "POST"])
def add_birthday():
    if request.method == "POST":

        # Get the form data
        first_name = request.form.get("firstName")
        birth_date = request.form.get("birthDate")
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
            "INSERT INTO birthdays (user_id, name, birth_date, day, month, year, display_on_main_page, email_notification) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)")
        data = (session["user_id"],
                first_name,
                birth_date,
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
def edit(id):
    if request.method == "POST":

        # Get the form data
        first_name = request.form.get("firstName")
        birth_date = request.form.get("birthDate")
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
            "UPDATE birthdays SET name = %s, birth_date = %s, day = %s, month = %s, year = %s, display_on_main_page = %s, email_notification = %s WHERE id = %s")
        data = (first_name,
                birth_date,
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
                         'display_on_main_page': birthday[7],
                         'email_notification': birthday[8]}

        return render_template('edit-birthday.html', birthday=birthday_dict)


@app.route('/delete/<int:id>', methods=["GET"])
def delete(id):

    if request.method == "GET":
        query = ("DELETE FROM birthdays WHERE id = %s")
        cursor.execute(query, (id,))
        connection.commit()
        return redirect('/list-birthdays')


@app.route("/list-birthdays", methods=["GET"])
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
            datetime_object = datetime.datetime.strptime(str(b[5]), "%m")
            full_month_name = datetime_object.strftime("%B")
            birthdays_dict.append({'id': b[0],
                                   'name': b[2],
                                   'birth_date': b[3],
                                   'day': b[4],
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
