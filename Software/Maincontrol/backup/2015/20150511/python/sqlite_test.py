#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Process data image management
import sqlite3

 # Create a database in RAM
db = sqlite3.connect(':memory:')

# Get a cursor object
cursor = db.cursor()
cursor.execute('''CREATE TABLE pdi(
                  id INTEGER PRIMARY KEY, 
                  tagProcess TEXT, 
                  tagUI TEXT,
                  valueR REAL,
                  valueT TEXT,
                  valueType TEXT,
                  domain TEXT,
                  source TEXT,
                  deviceID INTEGER,
                  permUIread INTEGER,
                  permUIwrite INTERGER,
                  low REAL,
                  high REAL,
                  zone TEXT,
                  subZone TEXT,
                  room TEXT,
                  ioType
                  )''')
db.commit()


cursor = db.cursor()

=====> weiter machen: Tabelle befüllen  
# Insert user 1
cursor.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(?,?,?,?)''', (name1,phone1, email1, password1))
print('First user inserted')

"""
#Inser dictionary values
cursor.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(:name,:phone, :email, :password)''',
                  {'name':name1, 'phone':phone1, 'email':email1, 'password':password1})
"""

db.commit()

#Retrieving Data (SELECT) with SQLite
cursor.execute('''SELECT name, email, phone FROM users''')
for row in cursor:
    # row[0] returns the first column in the query (name), row[1] returns email column.
    print('{0} : {1}, {2}'.format(row[0], row[1], row[2]))
    
    
# Update user with id 1
newphone = '3113093164'
userid = 1
cursor.execute('''UPDATE users SET phone = ? WHERE id = ? ''',
 (newphone, userid))
  
db.commit()

# Close the db connection
db.close()