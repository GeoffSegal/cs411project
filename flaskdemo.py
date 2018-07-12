#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.debug = True

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'movies'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route("/")
def index():
    return render_template('index2.html')

@app.route('/showmovies', methods = ['GET'])
def showmovies():
	with app.app_context():
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM movies")
		rows = cur.fetchall()
		cur.close()
		return render_template('showmovies.html', data=rows)


if __name__ == "__main__":
    app.run(host='0.0.0.0')

