from flask import redirect, session
from functools import wraps


def split_date(date):
    """
    Split date YYYY-MM-DD into seperate values 

    As a return value you get a dictionary with three key-value pairs:
    Keys: day, month and year
    """

    # Split the date using the string split method with the separator -
    year, month, day = date.split('-')

    # Return a dictionary
    return {'day': day, 'month': month, 'year': year}


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
