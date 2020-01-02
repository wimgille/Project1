import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import searchBooks

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user including password"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", message="must provide username"), 400

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message="must provide password"), 400

        # Ensure password confirmation was submitted match
        elif not request.form.get("confirmation"):
            return render_template("apology.html", message="please confirm password"), 400

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()

        # Ensure username does not exist
        if len(rows) == 1:
            return render_template("apology.html", message="user already exists"), 400

        # Check if the password and the confirmation password match
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("apology.html", message="Password and confirmation dont match"), 400

        pw_hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username,hash) VALUES (:name,:hash_value)",
                   {"name": request.form.get("username"),
                   "hash_value": pw_hash})

        db.commit()

        # Redirect user to success page
        return render_template("success.html", message="Well done")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", message="must provide username"), 400
 
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message="must provide password"), 400

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", message="invalid username and/or password"), 400

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/books")
def books():
    return render_template("search.html")


@app.route("/books/<int:book_id>")
def book(book_id):
    # Make sure the book exists.
    book = db.execute("SELECT * FROM books WHERE book_id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("apology.html", message="No such book.")
    else:
        return render_template("book.html", book=book)



@app.route("/search", methods=["GET", "POST"])
def search():
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        bookISBN = request.form.get("isbn")
        bookTitle = request.form.get("title")
        bookAuthor = request.form.get("author")

        results = searchBooks(bookISBN,bookTitle,bookAuthor)
        
        
        if bookISBN == "" and bookTitle == "" and bookAuthor == "":
            return render_template("apology.html", message="must provide at least one search term"), 400
        elif len(results) == 0:
            return render_template("apology.html", message="search criteria not found in the database"), 400
        else:
            return render_template("searchResults.html", books = results)
 
    
    else:
        return render_template("search.html")
