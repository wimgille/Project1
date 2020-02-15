#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18, 2019
@author: wimgille
"""
import os
import requests
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from bs4 import BeautifulSoup

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def searchBooks(bookISBN, bookTitle, bookAuthor):
    """  This function searches for a book in the database and returns a list of all the matching books  """

    # Users can search on ISBN, Title and Author. Also partial matches are included
    results = []
    if bookISBN != "":
        results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",
                    {"isbn": '%'+bookISBN+'%'}).fetchall()
    if bookTitle != "":
        resultsT = db.execute("SELECT * FROM books WHERE title LIKE :title",
                    {"title": '%'+bookTitle+'%'}).fetchall()
        results.extend(resultsT)    
    if bookAuthor != "":
        resultsA = db.execute("SELECT * FROM books WHERE author LIKE :author",
                    {"author": '%'+bookAuthor+'%'}).fetchall()
        results.extend(resultsA)
    
    # Remove all duplicate books in the list
    results = removeDuplicates(results)  
    return results

def removeDuplicates(oldList): 
    """ This function removes all duplicates from a list """
    
    newList = [] 
    for element in oldList: 
        if element not in newList: 
            newList.append(element) 
    return newList

def GetRatings(isbn):
    """ This functions calls the goodreads API and retrieves the avg rating and the number of ratings for any given isbn nr"""

    # Collect the XML file using the Goodreads API    
    url = 'https://www.goodreads.com/book/isbn/'+isbn+'?key=tWoJxAvYuLuEfOcSKkUOLw'
    response = requests.get(url)
    soup = BeautifulSoup(response.content,'xml')

    # From the API find the number of ratings and calculate the average
    rating_sum = int(soup.find('ratings_sum').get_text())
    rating_counter = int(soup.find('ratings_count').get_text())
    rating_avg = round(rating_sum/rating_counter,2)

    # Return the rating avg and the number of ratings in a list
    rating_tot = [rating_avg, rating_counter]
    return rating_tot
