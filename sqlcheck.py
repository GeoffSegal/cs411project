#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.debug = True

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'movies'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
with app.app_context():
	print (mysql)

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM movies")
	rows = cur.fetchall()
	cur.close()
	for row in rows:
		print (row['title'], row['year_released'], row['rating'])


