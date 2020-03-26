import os
import datetime

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

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
		name = request.form.get("user").capitalize()
		email = request.form.get("email")
		password = request.form.get("password")
		print(name + ", "+ email + ", " + password)
		dt = datetime.datetime.now()
		return render_template("index.html",name=name)
	return render_template("registration.html")


