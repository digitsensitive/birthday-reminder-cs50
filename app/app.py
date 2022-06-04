from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import sqlite3

from werkzeug.security import generate_password_hash

# Create a Flash instance
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Create a connection and cursor object to represent the database
database_users_connection = sqlite3.connect(
    'users.db', check_same_thread=False)
database_users = database_users_connection.cursor()

# Configure Sessions
Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()


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
        user_exists = database_users.execute(
            'SELECT EXISTS(SELECT 1 FROM users WHERE username=?)', [username])

        user_exists = user_exists.fetchone()[0]
        if user_exists == 1:
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
        database_users.execute('INSERT INTO users (username, hash) VALUES(?, ?)', (
                               username, generate_password_hash(password)))
        database_users_connection.commit()

        return redirect("/")
    return render_template("register.html")
