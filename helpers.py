#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18, 2019
@author: wimgille
"""
import numpy as np
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def searchBooks(bookISBN, bookTitle, bookAuthor):
 
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
      
    return results
