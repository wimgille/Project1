#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:46:16 2019

@author: wimgille
"""

import numpy as np
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# open the file
path = os.getcwd()
fileName = (path+r'/books.csv')
bookList = pd.read_csv(fileName)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

for i in range(len(bookList)):

    bookISBN = bookList.at[i,'isbn']
    bookTitle = bookList.at[i,'title']
    bookAuthor = bookList.at[i,'author']
    bookYear = int(bookList.at[i,'year'])

    rows = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                    {"isbn": bookISBN}).fetchall()
    
    if len(rows) == 0:
        print("not in the database yet")
        db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",
                   {"isbn": bookISBN,
                   "title": bookTitle,
                   "author": bookAuthor,
                   "year": bookYear})
        db.commit()
        print(f"added a book with isbn number: {bookISBN}")
    else:
        print("already in the database")

    

