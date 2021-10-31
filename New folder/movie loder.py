import requests,json,csv,os,sqlite3
import tmdbv3api

from tmdbv3api import TMDb
import json
import requests
tmdb = TMDb()
tmdb.api_key = 'bf048b0e274f5a9ee17fa19066dfc3ed'
tmdb.language = 'en'
#people in movie
#https://api.themoviedb.org/3/movie/123/credits?api_key=bf048b0e274f5a9ee17fa19066dfc3ed

from tmdbv3api import Movie
movie = Movie()

def get_genre(x):
    z,seq=[],['title','id','imdb_id','genres','tagline','poster_path','popularity','release_date','vote_average','vote_count','overview']
    m = movie.details(int(x))
    try:
        z.append(m.title)
        z.append(m.id)
        z.append(m.imdb_id)
        gen=''
        print(m.genres)
        for gen_name in m.genres:
            gen=gen_name['name']+';'+gen
        z.append(gen)
        z.append(m.tagline)
        z.append(m.poster_path)
        z.append(m.popularity)
        z.append(m.release_date)
        z.append(m.vote_average)
        z.append(m.vote_count)
        z.append(m.overview)
        print(m.title,x)
    except:
        z.append(' ')
    return z

def get_actor(x):
    m = movie.details(int(x))
    z=m.casts
    con = sqlite3.connect("app- ver 1.db")
    cur = con.cursor()
    if len(z['cast'])>0:
        if len(z['cast'])>0:
            top_cast = [0,1,2,3,4,5,6,7,8,9]
        else:
            top_cast = [0,1,2,3,4]
        for i in top_cast:
            print(z['cast'][i]['name'])

    
f= open('movie_ids_04_13_2021.json',encoding="utf8")
dataset=json.load(f)
#print(get_genre(dataset['data'][0]['id']))
sk=0
print(len(dataset['data']))
for i in dataset['data']:
    con = sqlite3.connect("app- ver 1.db")
    cur = con.cursor()
    z=cur.execute("select Tmbd_id from movie where Tmbd_id = ?",[i['id']]).fetchall()
    if z==[]:
        print(sk,end=" ")
        sk=sk+1
        lst=get_genre(i['id'])
        cur.execute("insert into `movie` (`name`,`Tmbd_id`,`Imbd_id`,`Geners`,`tagline`,`image_url`,`popularity`,`relased`,`vote avg`,`vote count`,`overview`) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",lst) 
    con.commit()
    
