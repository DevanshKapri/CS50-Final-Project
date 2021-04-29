import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(country):
    """Look up covid-19 stats for country."""

    # if user has not provide any country, look for all data
    if country == "WORLD":
        url = "https://covid-19-data.p.rapidapi.com/totals"

        # Contact API
        try:
            querystring = {"format": "json"}
            api_key = os.environ.get("API_KEY")
            headers = {
                'x-rapidapi-key': str(api_key),
                'x-rapidapi-host': "covid-19-data.p.rapidapi.com"
            }
            response = requests.request("GET", url, headers=headers)
            response.raise_for_status()
        except requests.RequestException:
            return None

    else:
        url = "https://covid-19-data.p.rapidapi.com/country"
        querystring = {"name": country}

        # Contact API
        try:
            api_key = os.environ.get("API_KEY")
            headers = {
                'x-rapidapi-key': str(api_key),
                'x-rapidapi-host': "covid-19-data.p.rapidapi.com"
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
        except requests.RequestException:
            return None

    # Parse Response
    try:
        query = response.json()
        return {
            "confirmed": query[0]["confirmed"],
            "recovered": query[0]["recovered"],
            "critical": query[0]["critical"],
            "deaths": query[0]["deaths"],
            "lastUpdate": query[0]["lastUpdate"]
        }
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def inr(value):
    """Formats value as INR."""
    return f"₹{value:,.2f}"