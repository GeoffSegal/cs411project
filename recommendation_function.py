import pymysql
def recommend(user):

	conn = pymysql.connect("localhost","root","","movies")
	cur = conn.cursor()

	cur.execute("SELECT movie_id from movies order by movie_id;")
	potentialmovies = [ x[0] for x in cur.fetchall()]

	cur.execute("SELECT actor_id from actors, favorites where actors.movie_id = favorites.movie_id and user_id=\'{}\';".format(user))
	actors = [ x[0] for x in cur.fetchall() ]
	
	print(len(actors))
	cur.execute("SELECT genre from movies, favorites where movies.movie_id = favorites.movie_id and user_id=\'{}\';".format(user))
	genres = [ x[0] for x in cur.fetchall()]

	print(len(genres))
	cur.execute("SELECT director from directors, favorites where directors.movie_id = favorites.movie_id and user_id=\'{}\';".format(user))
	directors = [ x[0] for x in cur.fetchall()]
	
	print(len(directors))

	points = [0]*len(potentialmovies)

	for idx in range(len(genres)):
		cur.execute("SELECT movie_id, case when genre = \'{}\' then 20 else 0 end from movies ORDER BY movie_id".format(genres[idx]))
		temp_points = [x[1] for x in cur.fetchall()]
		points = [x+y for x,y in zip(points,temp_points)]
		
	for idx in range(len(actors)):
		cur.execute("SELECT movie_id, case when movie_id IN(select movie_id from actors where actor_id = \'{}\') then 30 else 0 end from movies ORDER BY movie_id".format(actors[idx]))
		temp_points = [x[1] for x in cur.fetchall()]
		points = [x+y for x,y in zip(points,temp_points)]
		
	for idx in range(len(directors)):
		cur.execute("SELECT movie_id, case when movie_id IN(select movie_id from directors where director = \'{}\') then 50 else 0 end from movies ORDER BY movie_id".format(directors[idx]))	
		temp_points = [x[1] for x in cur.fetchall()]
		points = [x+y for x,y in zip(points,temp_points)]
		

	conn.close()

	Z = [x for _,x in sorted(zip(points,potentialmovies), reverse=True)]
	
	print(len(Z))
	Z = Z[:5]
	print(len(Z))
	
	print(Z)
	

	return Z


recommend('aa1234')
