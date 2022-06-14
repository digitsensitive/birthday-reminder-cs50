import datetime
from flask import redirect, session
from functools import wraps


def get_month_name(month: int):
    """
    Convert month int to string.
    """
    datetime_object = datetime.datetime.strptime(str(month), "%m")
    return datetime_object.strftime("%B")


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
