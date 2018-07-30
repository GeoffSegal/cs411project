
def recommend():
	import pymysql
	import pandas as pd


	conn = pymysql.connect("localhost","root","","movies")
	cur = conn.cursor()

	start_time = datetime.now()

	cur.execute("SELECT actor_id from actors, favorites where actors.movie_id = favorites.movie_id and user_id=\'{}\';".format(session['username']))
	actors = [ x[0] for x in cur.fetchall() ]

	cur.execute("SELECT genre from movies, favorites where movies.movie_id = favorites.movie_id and user_id=\'{}\';".format(session['username']))
	genres = [ x[0] for x in cur.fetchall()]

	cur.execute("SELECT director from directors, favorites where directors.movie_id = favorites.movie_id and user_id=\'{}\';".format(session['username']))
	directors = [ x[0] for x in cur.fetchall()]

	cur.execute("SELECT movie_id from favorites where user_id=\'{}\';".format(session['username']))
	favorites = [ x[0] for x in cur.fetchall()]


	format_strings = ','.join(['%s']*len(genres))
	cur.execute("SELECT movie_id from movies where genre IN (%s)" % format_strings, tuple(genres))
	temp_genres = [x[0] for x in cur.fetchall()]

	format_strings = ','.join(['%s']*len(actors))
	cur.execute("SELECT movie_id from actors where actor_id in (%s)" % format_strings, tuple(actors))
	temp_actors = [x[0] for x in cur.fetchall()]

	format_strings = ','.join(['%s']*len(directors))
	cur.execute("SELECT movie_id from directors where director in(%s)" % format_strings, tuple(directors))
	temp_directors = [x[0] for x in cur.fetchall()]




	all_movies = temp_genres + temp_actors + temp_directors
	all_points = [20]*len(temp_genres) + [30] * len(temp_actors) + [50] * len(temp_directors)

	df1 = pd.DataFrame( {'movie_id': all_movies, 'points': all_points})
	df2 = df1.groupby('movie_id')['points'].sum()
	df3 = df2.reset_index()
	df4 = df3[~df3['movie_id'].isin(favorites)]


	recommendedMovies = df4.sort_values(by=['points'], ascending=False)['movie_id'][:5]

	cur.execute("DELETE FROM recommended where user_id = \'{}\';".format(session['username'])
	for idx in range(len(recommendedMovies)):
		cur.execute("INSERT INTO recommended (user_id, movie_id) VALUES(\'{}\',\'{}\');".format(session['username'],recommendedMovies[idx])

	conn.close()

