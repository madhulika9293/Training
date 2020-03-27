import os
import datetime
import logging

from flask import Flask, session, render_template, request
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

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
	name = "Guest"
	return render_template("index.html",name=name)

@app.route("/register", methods=["GET","POST"])
def register():
	if (request.method == "POST"):
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
	return render_template("registration.html")

@app.route("/admin",methods=["GET"])
def admin():
	allusers = User.query.all()
	logging.info(allusers)
	return render_template("admin.html",allusers=allusers)

