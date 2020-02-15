# Project1
Project1 on CS50W 2019. In this project, we’ll build a book review website.

application.py is the main Flask application, should you require the database URI, just let me know.

In this application users can find the following elements:
0) Registration, Login and Logout. Passwords are hashed using werkzeug
1) There is a database with 5,002 books to search on 
2) Users can search for a book based on ISBN number, title and / or the author of a book. On the search results page, users can click through to see the details of a book on the Book Page
3) Book Page: This page shows details on a the book: its title, author, publication year, ISBN number, and any reviews that users might have left for the book on the  website.
4) On the book page, users can submit a review consisting of a rating on a scale of 1 to 5, as well as a text component
5) The Book Page also contains data from Goodreads, which have been retrieved using an API
6) API Access: Users can make a GET request to the website's /api/<isbn> route, where <isbn> is an ISBN number. If the ISBN number is in the database, the API returns a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.