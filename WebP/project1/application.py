import os
import datetime
import logging

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

#Setup logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
	__tablename__ = "users"
	fname = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False, primary_key=True)
	password = db.Column(db.String, nullable=False)
	timestamp = db.Column(db.DateTime, nullable=False)

class Book(db.Model):
    __tablename__ = "books"
    # id = db.Column(db.Integer, primary_key = True, nullable = False)
    isbn = db.Column(db.String, primary_key = True, nullable = False)
    title = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.Integer, nullable = False)

    def __init__(self, isbn, title, author, year):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
	name = "Guest"
	return render_template("index.html",name=name)

@app.route("/register", methods=["GET","POST"])
def register():
	if (request.method=="POST" and request.form.get('action') == "Register"):
		fname = request.form.get("user").capitalize()
		email = request.form.get("email")
		password = request.form.get("password")
		logging.info(fname)
		if not fname:
			return render_template("error.html",message="Please provide username")
		elif not email:
			return render_template("error.html",message="Please provide email")
		elif not password:
			return render_template("error.html",message="Please provide password")
		else:
			dt = datetime.datetime.now()
			userVerify = User.query.filter_by(email=email)
			if userVerify:
				return render_template("error.html",message="You are already registered!")
			else:
				user = User(fname=fname,email=email,password=password,timestamp=dt)
				db.session.add(user)
				db.session.commit()
				return render_template("index.html",name=fname) # index page with username if successful, for now
	elif (request.method=="POST" and request.form.get('action') == "Login"):
		fname = request.form.get("user").capitalize()
		email = request.form.get("email")
		password = request.form.get("password")
		logging.info(request.form.get('action'))
		return redirect(url_for("auth",fname=fname,email=email,password=password))
	return render_template("registration.html")

@app.route("/admin",methods=["GET"])
def admin():
	allusers = User.query.all()
	logging.info(allusers)
	return render_template("admin.html",allusers=allusers)

@app.route("/auth", methods = ["POST"])
def auth():

    # Tries to see whether the user provided the details correct or not.
    # Otherwise will redirect to login page.
    if request.method == "POST":
        try:
            session['name'] = request.form.get("name")
            
            if not session['name']:
                return render_template("error.html", message="Please provide User name.")
            if not request.form.get("password"):
                return render_template("error.html", message="Please provide Password.")
            data = User.query.filter_by(name=session['name']).one()
            
            if check_password_hash(data.password, request.form.get("password")):
                return redirect("/")
            else:
                return render_template("error.html",
                    message = """Invalid Username and(or) password""")
        except:
            session.clear()
            return render_template("error.html", 
                message = """You might not be registered user. Please register first""")
@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")