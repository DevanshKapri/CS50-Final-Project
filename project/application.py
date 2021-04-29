import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, inr, lookup

# Flask config
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# custom filter
app.jinja_env.filters["inr"] = inr
app.jinja_env.globals.update(inr=inr, lookup=lookup, int=int)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///covaccine.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # clearing previous sessions
    session.clear()
    # Reconnect to the database
    db = None
    db = SQL("sqlite:///covaccine.db")

    # if user requests for the login page
    if request.method == "GET":
        return render_template("login.html")
    # if user enters credentials for login
    else:
        email = request.form.get("email").lower()
        # checking for email
        if not email:
            return apology("Must provide email.", 403)
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", email)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    email = request.form.get("email").lower()

    if request.method == "POST":
        if not email:
            return apology("must provide email", 400)

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password", 400)

        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords and confirmation don't match", 400)
        elif len(request.form.get("password")) < 4 or request.form.get("password").isdigit() or request.form.get("password").islower() or request.form.get("password").isupper() or request.form.get("password").isalpha() or request.form.get("password").isalnum():
            return apology("Password must be at least 4 characters long, with at least one lowercase and  one upper case alphabet, one number and one special character.", 400)

        else:
            if len(db.execute("SELECT * FROM users WHERE username = ?", email)) == 0:
                query = db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", email,
                                   generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8))
                session["user_id"] = query

                return redirect("/")

            else:
                return apology("Email already exists.", 400)

    else:
        flash("Welcome to Covaccine! Please enter username and password to register.")
        return render_template("register.html")


@app.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html")


@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    """Let user change the password"""
    if request.method == "GET":
        return render_template("changepw.html")

    else:
        rows = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])

        if not request.form.get("oldpw"):
            return apology("Missing current password!", 400)

        if not check_password_hash(rows[0]["hash"], request.form.get("oldpw")):
            return apology("Incorrect current password.", 400)

        if not request.form.get("password"):
            return apology("Missing password!", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match!", 400)

        elif len(request.form.get("password")) < 4 or request.form.get("password").isdigit() or request.form.get("password").islower() or request.form.get("password").isupper() or request.form.get("password").isalpha() or request.form.get("password").isalnum():
            return apology("Password must be at least 4 characters long, with at least one lowercase and  one upper case alphabet, one number and one special character.", 403)

        else:
            pwdhash = generate_password_hash(request.form.get("password"))
            db.execute("UPDATE users SET hash = :hash WHERE id=:id", hash=pwdhash, id=session["user_id"])
            flash("Password changed!")
            return redirect("/profile")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    rows = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    name = rows[0]["name"]
    email = rows[0]["username"]
    cash = rows[0]["cash"]
    country = rows[0]["country"]

    if request.method == "GET":
        return render_template("profile.html", name=name, email=email, cash=cash, country=country)

    else:
        new_email = request.form.get("email").lower()
        new_name = request.form.get("name")
        new_country = request.form.get("country")

        if new_email != None and len(db.execute("SELECT * FROM users WHERE username = ?", new_email)) != 0:
            return apology("Email already exists.", 404)

        if not new_email:
            new_email = email

        if not new_name:
            new_name = name
        if not new_country:
            new_country = country

        db.execute("UPDATE users SET (username, name, country) = (?, ?, ?) WHERE id = ?",
                   new_email, new_name, new_country, session['user_id'])

        flash("Profile details updated.")
        return redirect("/profile")


@app.route("/tracker", methods=["GET", "POST"])
@login_required
def tracker():

    if request.method == "GET":
        row = db.execute("SELECT country FROM users where id = ?", session['user_id'])
        country = (row[0]["country"]).upper()

    else:
        country = request.form.get("search").upper()

    info = lookup(country)
    if not info:
        country = "WORLD"
        info = lookup(country)
        flash("Country doesn't exist in database.")
        return render_template("tracker.html", info=info, country=country)
    else:
        return render_template("tracker.html", info=info, country=country)


@app.route("/donate", methods=["GET", "POST"])
@login_required
def donate():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    name = rows[0]["name"]
    email = rows[0]["username"]
    cash = rows[0]["cash"]

    if request.method == "GET":
        return render_template("donate.html", name=name, email=email, cash=cash)
    else:

        # getting donation amount
        amount = float(request.form.get("amount"))

        # ensuring amt is not empty
        if not amount:
            return apology("Must provide donation amount.", 400)
        # ensure password exists
        if not request.form.get("password"):
            return apoology("Must provide password.", 400)
        # ensurig password matches
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Incorrect password.", 400)

        user = session['user_id']
        money = db.execute("SELECT cash FROM users WHERE id = ?", user)
        cash = money[0]["cash"]

        # checking for cash
        if amount > cash:
            flash("Insufficient balance. Please add money to your wallet.")
            return redirect("/wallet")
        else:
            balance = cash - amount
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.execute("INSERT INTO transactions (person_id, donation, transacted) VALUES (?, ?, ?)",
                       user, -amount, timestamp)
            db.execute("INSERT INTO donations (donator_id, amount) VALUES (?, ?)", user, amount)
            db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, user)
            row = db.execute("SELECT SUM(amount) as total FROM donations")
            donations = row[0]["total"]
            flash("Donation successful!")
            return render_template("thanks.html", donations=donations)


@app.route("/wallet", methods=["GET", "POST"])
@login_required
def wallet():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])

    if request.method == "GET":
        history = db.execute(
            "SELECT transct_id, donation, transacted FROM transactions WHERE person_id = ? ORDER BY transct_id DESC", session['user_id'])
        money = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        cash = money[0]["cash"]

        return render_template("wallet.html", history=history, cash=cash)

    else:

        # getting amount to be added
        amount = float(request.form.get("amount"))

        # ensuring amt is not empty
        if not amount:
            return apology("Must provide donation amount.", 400)
        # ensure password exists
        if not request.form.get("password"):
            return apoology("Must provide password.", 400)
        # ensurig password matches
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Incorrect password.", 400)

        money = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        cash = money[0]["cash"]
        cash += amount
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session['user_id'])
        db.execute("INSERT INTO transactions (person_id, donation, transacted) VALUES (?, ?, ?)",
                   session['user_id'], amount, timestamp)

        flash("Amout added successfully!")
        return redirect("/profile")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
