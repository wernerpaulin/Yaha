#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

 # Create a database in RAM
db = sqlite3.connect(':memory:')

# Get a cursor object
cursor = db.cursor()
cursor.execute('''CREATE TABLE users(
                  id INTEGER PRIMARY KEY, 
                  name TEXT, 
                  phone TEXT, 
                  email TEXT unique, 
                  password TEXT)''')
db.commit()


cursor = db.cursor()
name1 = 'Andres'
phone1 = '3366858'
email1 = 'user@example.com'
password1 = '12345'
 
name2 = 'John'
phone2 = '5557241'
email2 = 'johndoe@example.com'
password2 = 'abcdef'
 
# Insert user 1
cursor.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(?,?,?,?)''', (name1,phone1, email1, password1))
print('First user inserted')
 
# Insert user 2
cursor.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(?,?,?,?)''', (name2,phone2, email2, password2))
print('Second user inserted')

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