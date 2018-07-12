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
		moviesearch = request.args.get('movie')
		cur = mysql.connection.cursor()
		cur.execute(("select title, movie_id, full_name as director, rating from movies, directors, ratings, names where movies.movie_id = directors.movie_id AND DIRECTOR = name_id AND movies.movie_id = ratings.movie_id AND title LIKE '%{}%';").format(moviesearch))
		rows = cur.fetchall()
		cur.close()
		return render_template('showmovies.html', data=rows)

def addfavorites():
	with app.app_context():
		moviesearch = request.args.get('favmovie')
		cur = mysql.connection.cursor()
		cur.execute(("INSERT INTO favorites (user_id, movie_id) VALUES ('aa1234', '{}';).format(moviesearch))
		cur.commit()
		cur.execute(("select title from movies, favorites where movies.movie_id = favorites.movie_id AND favorites.user_id = 'aa1234'))
		rows = cur.fetchall()
		cur.close()
		return render_template('shofavorites.html', data=rows)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
