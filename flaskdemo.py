#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for, request, session
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from hashlib import md5
import os
from sqlalchemy.orm import sessionmaker
 

app = Flask(__name__)
app.secret_key = 'secret'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'movies'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
 
@app.route('/')
def home():
    if 'username' not in session:
        return render_template('login.html')

    username_session = (session['username']).capitalize()
    #username_session = escape(session['username']).capitalize()
    return render_template('index2.html', session_user_name=username_session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return render_template('index2.html')

    error = None
    try:
        if request.method == 'POST':
	    username_form  = request.form['username']
	    #password_form = sha256_crypt.hash(str(request.form['password']))
            password_form = request.form['password']
            cur = mysql.connection.cursor()
	    cur.execute('SELECT username FROM user WHERE username = "{}";'.format(username_form))
	    if not cur.fetchone():
	        raise Exception('Invalid username')
	    else:
	        cur.execute('SELECT password FROM user WHERE username = "{}" AND password = "{}";'.format(username_form, password_form))
	        if cur.fetchone():
		    cur.close()
	            session['username'] = username_form
	            return render_template('index2.html')
                cur.close()
                raise Exception(password_form)
	    #raise Exception('Invalid password')
    except Exception as e:
        error = str(e)

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('login.html')

@app.route('/register', methods = ['GET'])
def register():
    return render_template('register.html')

@app.route('/registration', methods = ['POST'])
def registration():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
    cur = mysql.connection.cursor()
    error = None
    cur.execute(('SELECT 1 FROM user WHERE username="{}";').format(POST_USERNAME))
    if cur.fetchone():
        error = "username already exists"
        cur.close()
        return render_template('register.html', error=error)
    else:
        cur.execute(("INSERT INTO user (username, password) VALUES ('{}', '{}');").format(POST_USERNAME, POST_PASSWORD))
	mysql.connection.commit()
	cur.close()
        return render_template('login.html')

@app.route('/showmovies', methods = ['GET'])
def showmovies():
	with app.app_context():
		moviesearch = request.args.get('movie')
		cur = mysql.connection.cursor()
		cur.execute(("select title, movies.movie_id, full_name as director, rating from movies, directors, ratings, names where movies.movie_id = directors.movie_id AND DIRECTOR = name_id AND movies.movie_id = ratings.movie_id AND title LIKE '%{}%';").format(moviesearch))
		rows = cur.fetchall()
		cur.close()
		return render_template('showmovies.html', data=rows)

@app.route('/showfavorites', methods = ['GET'])
def showfavorites():
	with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute(("select DISTINCT title, movies.movie_id, rating from movies, favorites where movies.movie_id = favorites.movie_id AND favorites.user_id = '{}';").format(session['username']))

                rows = cur.fetchall()
                cur.close()
                return render_template('showfavorites.html', data=rows)

@app.route('/addfavorites', methods = ['POST', 'GET'])
def addfavorites():
	with app.app_context():
		moviesearch = request.args.get('favmovie')
		cur2 = mysql.connection.cursor()
		cur2.execute(('SELECT 1 FROM favorites WHERE movie_id="{}";').format(moviesearch))
		if not cur2.fetchone():
			cur2.execute(("INSERT INTO favorites (user_id, movie_id) VALUES ('{}', '{}');").format(session['username'], moviesearch))
		mysql.connection.commit()
		cur2.close()
		cur = mysql.connection.cursor()
		cur.execute(("select DISTINCT title, movies.movie_id, rating from movies, favorites where movies.movie_id = favorites.movie_id AND favorites.user_id = '{}';").format(session['username']))
		rows = cur.fetchall()
		cur.close()
		return render_template('showfavorites.html', data=rows)

@app.route('/removefavorites', methods = ['POST', 'GET'])
def removefavorites():
	with app.app_context():
                moviesearch = request.args.get('favmovie')
                cur2 = mysql.connection.cursor()
                cur2.execute(("DELETE FROM favorites WHERE user_id = '{}' AND movie_id = '{}';").format(session['username'], moviesearch))
                mysql.connection.commit()
                cur2.close()
                cur = mysql.connection.cursor()
                cur.execute(("select DISTINCT title, movies.movie_id, rating from movies, favorites where movies.movie_id = favorites.movie_id AND favorites.user_id = '{}';").format(session['username']))
                rows = cur.fetchall()
                cur.close()
                return render_template('showfavorites.html', data=rows)

@app.route('/ratefavorites', methods = ['POST', 'GET'])
def ratefavorites():
	with app.app_context():
                moviesearch = request.args.get('favmovie')
                movierating = request.args.get('movierating')
                cur2 = mysql.connection.cursor()
                cur2.execute(("UPDATE favorites set rating = {} WHERE user_id = '{}' AND movie_id = '{}';").format(movierating, session['username'], moviesearch))
                mysql.connection.commit()
                cur2.close()
                cur = mysql.connection.cursor()
                cur.execute(("select DISTINCT title, movies.movie_id, rating from movies, favorites where movies.movie_id = favorites.movie_id AND favorites.user_id = '{}';").format(session['username']))
                rows = cur.fetchall()
                cur.close()
                return render_template('showfavorites.html', data=rows)

@app.route('/conversations', methods = ['GET'])
def getConversations():
        with app.app_context():
                user = session['username']
                cur = mysql.connection.cursor()
                cur.execute(("SELECT * FROM (SELECT DISTINCT to_userid FROM messages WHERE (from_userid = '{}' OR to_userid = '{}') UNION SELECT DISTINCT from_userid FROM messages WHERE (from_userid = '{}' OR to_userid = '{}')) AS t WHERE t.to_userid <> '{}';").format(user, user, user, user, user))
                rows = cur.fetchall()
                cur.close()
		
		return rows

@app.route('/sendMessage', methods = ['POST'])
def sendMessage():
        with app.app_context():
		#arguments
                sender = session['username']
		recipient = request.args.get['recipient']
		#validate the recipient username?
		body = request.form['messageBody']
		
		#post new message
                cur = mysql.connection.cursor()
                cur.execute(("INSERT INTO messages (from_userid, to_userid, message_body) VALUES ('{}', '{}', '{}');").format(user, recipient, body))
                cur.close()

		#query latest messages
		cur2 = mysql.connection.cursor()
		cur2.execute(("SELECT * FROM (SELECT * FROM messages WHERE (from_userid = '{}' OR from_userid = '{}') AND (to_userid = '{}' OR to_userid = '{}') ORDER BY message_time DESC LIMIT 20) AS t  ORDER BY t.message_time;").format(user, recipient, user, recipient))
		rows = cur2.fetchall()
		cur2.close()

		return rows
		
@app.route('/messages', methods = ['GET'])
def getMessages():
	with app.app_context():
		user = session['username']
		recipient = request.args.get['recipient']
		#validate the recipient username?

		#query latest messages
		cur = mysql.connection.cursor()
		cur.execute(("SELECT * FROM (SELECT * FROM messages WHERE (from_userid = '{}' OR from_userid = '{}') AND (to_userid = '{}' OR to_userid = '{}') ORDER BY message_time DESC LIMIT 20) AS t  ORDER BY t.message_time;").format(user, recipient, user, recipient))
		rows = cur.fetchall()
		cur.close()

		return rows


if __name__ == "__main__":
    app.secret_key = os.urandom(50)
    app.run(debug=True,host='0.0.0.0', port=4000)

