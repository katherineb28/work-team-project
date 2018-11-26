import os
import re
import pandas as pd
from flask import Flask, jsonify, render_template, request, url_for, flash, redirect
from flask_jsglue import JSGlue


from cs50 import SQL
#Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    """Render map"""
    return render_template("index.html")

@app.route("/employees", methods=["GET", "POST"])
def employees():
    """Add new employee"""
    if request.method == "POST":
        try:
            name = request.form.get("first-name")
            last_name = request.form.get("last-name")
            role = request.form.get("role")
            email = request.form.get("email")
        except:
            return apology("enter some input")

        if not name:
            return apology("enter employee name")
        if not last_name:
            return apology("enter employee last name")
        if not role:
            return apology("enter employee role")
        if not email:
            return apology("enter employee email")
        if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
            return apology("enter a valid email address")


        db.execute("INSERT INTO employees (first_name,last_name,role,email) \
                    VALUES(:first_name, :last_name, :role, :email)", \
                    first_name = name, last_name=last_name, \
                    role = role, email = email)
        employees = db.execute("SELECT * FROM employees ORDER BY role ASC")
        total_employees = db.execute("SELECT COUNT(first_name) FROM employees")
        return redirect(url_for("employees"))
    employees = db.execute("SELECT * FROM employees ORDER BY role ASC")
    total_managers = db.execute("SELECT COUNT(role) FROM employees WHERE role = :role", role = "Manager")
    total_talents = db.execute("SELECT COUNT(role) FROM employees WHERE role = :role", role = "Talent")
    total_trainees = db.execute("SELECT COUNT(role) FROM employees WHERE role = :role", role = "Trainee")
    total_managers = total_managers[0]['COUNT(role)']
    total_talents = total_talents[0]['COUNT(role)']
    total_trainees = total_trainees[0]['COUNT(role)']
    return render_template("employees.html",employees = employees,  total_talents = total_talents,total_managers = total_managers, total_trainees = total_trainees)

@app.route("/requests", methods=["GET", "POST"])
def requests():
    """Add new request"""
    if request.method == "POST":
        try:
            name = request.form.get("name")
            day = int(request.form.get("day"))
            month = request.form.get("month")
            req= request.form.get("req")
        except:
            return apology("enter some input")

        if not name:
            return apology("enter employee name")
        if not day or day < 1 or day >31:
            return apology("enter valid day")
        if not month:
            return apology("enter month")
        if not req:
            return apology("enter request")

        employees = db.execute("SELECT * FROM employees ORDER BY first_name ASC")

        db.execute("INSERT INTO requests (requestee,day,month,req) \
                    VALUES(:requestee, :day, :month, :req)", \
                   requestee = name, day = day, \
                    month = month, req = req)

        return redirect(url_for("index"))
    employees = db.execute("SELECT * FROM employees ORDER BY first_name ASC")
    return render_template("requests.html", employees = employees)

@app.route("/template",methods=["GET"])
def template():
    """Create an example schedule"""

    morning = 7;
    evening = 15;
    night = 23;

    employees = db.execute("SELECT * FROM employees ORDER BY first_name ASC")
    return render_template("index.html",employees = employees)


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
