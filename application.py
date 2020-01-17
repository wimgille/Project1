import os
import datetime

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import searchBooks, GetRatings

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
    """Register new user including hashed password"""

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

    # Redirect user to home page
    return redirect("/")

@app.route("/books")
def books():
    # Work in progress. Redirect to search until we make a proper books page
    return render_template("search.html")


@app.route("/books/<int:book_id>")
def book(book_id):
    """Display the details of a book page"""
    
    # Make sure the book exists.
    book = db.execute("SELECT * FROM books WHERE book_id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("apology.html", message="No such book.")
    else:
        # Collect the reviews in our own dbse
        reviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book_id}).fetchall()


        # Collect the rating statistics from goodreads
        rating_tot = GetRatings(book.isbn)
        return render_template("book.html", book=book, rating=rating_tot)

@app.route("/submit", methods=["GET", "POST"])
def submitReview():
    """Submit a review for a book"""
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Check if the user already filled in a review, if so send an error message
        review = db.execute("SELECT review_id FROM reviews WHERE book_id = :book_id AND user_id = :user_id",
            {"book_id": request.form.get("book_id"),
            "user_id": session["user_id"]}).fetchone()
        if review:
            return render_template("apology.html", message="You already left a review for this book")
                
        # check if the form was filled in correctly
        if not request.form.get("rating_number"):
            return render_template("apology.html", message="You must provide a rating")
        if not request.form.get("rating_review"):
            return render_template("apology.html", message="You must provide a review")
        if not request.form.get("book_id") or not session["user_id"]:
            return render_template("apology.html", message="System error, book ID or user ID not known")
        
        else:
            # Update the database by adding the review in the database
            db.execute("INSERT INTO reviews (review_date, book_id, user_id, rating_nr, rating_txt) VALUES (:date,:book_id,:user_id,:rating_nr,:rating_txt)",
                    {"date": datetime.date.today(), 
                    "book_id": request.form.get("book_id"),
                    "user_id": session["user_id"],
                    "rating_nr": request.form.get("rating_number"),
                    "rating_txt": request.form.get("rating_review")})
            db.commit()
            # Redirect user to success page
            return render_template("success.html", message="Thanks for you review")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Collect search terms from the webform
        bookISBN = request.form.get("isbn")
        bookTitle = request.form.get("title")
        bookAuthor = request.form.get("author")

        # Select all books that match at least one of the search terms 
        results = searchBooks(bookISBN,bookTitle,bookAuthor)
        
        # Make sure at least one search term was committed and display the results if there are some
        if bookISBN == "" and bookTitle == "" and bookAuthor == "":
            return render_template("apology.html", message="must provide at least one search term"), 400
        elif len(results) == 0:
            return render_template("apology.html", message="search criteria not found in the database"), 400
        else:
            return render_template("searchResults.html", books = results)
 
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search.html")
