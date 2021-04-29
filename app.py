import hashlib
import json
import random
import sqlite3
import string
import requests
from flask import Flask, flash, redirect, render_template, request, url_for
from tmdbv3api import TMDb,Movie,Person

tmdb = TMDb()
tmdb.api_key = 'bf048b0e274f5a9ee17fa19066dfc3ed'
tmdb.language = 'en'
sk_api=input("enter api")
API_key='bf048b0e274f5a9ee17fa19066dfc3ed'
def rand_str():
    digits = string.digits
    letter_digit_list = list(string.digits + string.ascii_letters)
    random.shuffle(letter_digit_list)
    sample_str = ''.join((random.choice(digits) for i in range(6)))
    sample_str += ''.join((random.choice(letter_digit_list) for i in range(10)))
    aList = list(sample_str)
    random.shuffle(aList)
    final_str = ''.join(aList)
    return final_str

def get_stats(data):
    def conv_dict_prec(dict_input):
        ret_array=[]
        s = sum(dict_input.values())
        for k, v in dict_input.items():
            pct = round(v * 100.0 / s,2)
            ret_array.append({"y":pct, "label":str(k)})
        return ret_array
        
    gen_origin_dict={"genres":[{"id":28,"name":"Action"},{"id":12,"name":"Adventure"},{"id":16,"name":"Animation"},{"id":35,"name":"Comedy"},{"id":80,"name":"Crime"},{"id":99,"name":"Documentary"},{"id":18,"name":"Drama"},{"id":10751,"name":"Family"},{"id":14,"name":"Fantasy"},{"id":36,"name":"History"},{"id":27,"name":"Horror"},{"id":10402,"name":"Music"},{"id":9648,"name":"Mystery"},{"id":10749,"name":"Romance"},{"id":878,"name":"Science Fiction"},{"id":10770,"name":"TV Movie"},{"id":53,"name":"Thriller"},{"id":10752,"name":"War"},{"id":37,"name":"Western"}]}
    gen_dict,rate_dict=dict(),{'0':0,'1':0,'2':0,'3':0,'4':0,'5':0}
    ret=[]
    if data==[]:
        return []
    for i in data:
        #print(i[3])
        # 3 for genere if get data changed please change it too
        gen=i['genres'].split(';')
        for j in gen:
            if j!='':
                if j not in gen_dict:
                    gen_dict[j] = 1
                else:
                    gen_dict[j] += 1

        # 9 for user rating if get data changed please change it too
        rate=i['user_review']
        if rate=='':
            rate_dict[0]=rate_dict[0]+1
        else:
            rate_dict[rate]=rate_dict[rate]+1
            
    ret=[conv_dict_prec(gen_dict),conv_dict_prec(rate_dict)]
    #print(ret)
    return ret

def get_actor(x):
    movie = Movie()
    #print(dir(movie))
    m ,ret_lst= movie.details(int(x)),[]
    z=m.casts
    if len(z['cast'])>0:
        #print(z['cast'][0])
        if len(z['cast'])>0:
            top_cast = [0,1,2,3,4,5,6,7,8,9]
        else:
            top_cast = [0,1,2,3,4]
        for i in top_cast:
            #https://image.tmdb.org/t/p/original
            temp_lst={}
            for j in ['name','character','profile_path','id']:
                if j=='profile_path':
                    if z['cast'][i][j]!=None:
                        temp_lst[j]='https://image.tmdb.org/t/p/original'+z['cast'][i][j]
                    else:
                        temp_lst[j]='https://webstockreview.net/images/human-clipart-human-symbol-19.png'
                    continue
                temp_lst[j]=z['cast'][i][j]
            #print(temp_lst)
            ret_lst.append(temp_lst)
        return ret_lst


def get_popular_movies():
    movie = Movie()
    popular = movie.popular()
    lst=[]
    j=0
    for p in popular:
        ret_lst={}
        ret_lst['title']=p.title
        ret_lst['id']=p.id
        if p.poster_path==None:
            ret_lst['poster_path']='https://www.sundialhome.com/assets/images/noImage.jpg'
        else:
            ret_lst['poster_path']='https://image.tmdb.org/t/p/original'+p.poster_path
        ret_lst['popularity']=p.popularity
        j=j+1
        lst.append(ret_lst)
        if j>9:
            break
    return lst

def get_data_from_API(API_key, Movie_IDs): # get movie data from api
    text=[]
    data=[]
    user_review=[]
    posterpath='https://image.tmdb.org/t/p/original'
    for i in Movie_IDs:
        #print(i)
        query = 'https://api.themoviedb.org/3/movie/'+str(i[0])+'?api_key='+API_key+'&language=en-US'
        response =  requests.get(query)
        if response.status_code==200:
            array = response.json()
            text.append(array)
            user_review.append(str(i[1]))
    for i in range(len(text)):
        #if change in service_req please change stat to
        services=['title','id','imdb_id','genres','tagline','poster_path','popularity','release_date','vote_average','vote_count','overview']
        lst={}
        for req_service in services:
            if text[i][req_service] is None:
                if req_service=='poster_path':
                    lst['poster_path']='https://www.sundialhome.com/assets/images/noImage.jpg'
                else:
                    lst['poster_path']=' '
            elif req_service=='genres':
                gen=''
                for gen_name in text[i]['genres']:
                    gen=gen_name['name']+';'+gen
                lst['genres']=gen
            elif req_service=='poster_path':
                lst['poster_path']=str(posterpath+text[i]['poster_path'])
            else:
                lst[req_service]=text[i][req_service]
        lst['user_review']=user_review[i]
        data.append(lst)
            
    return data

def get_about_actors(x):
    person_ret={}
    people = Person()
    p=people.details(int(x))
    person_ret["name"]=p.name
    person_ret["birthday"]=p.birthday
    person_ret["place_of_birth"]=p.place_of_birth
    person_ret["profile_path"]='https://image.tmdb.org/t/p/original'+str(p.profile_path)
    person_ret["popularity"]=p.popularity
    person_ret["biography"]=p.biography
    #person_ret["movies"]=[]
    p=people.movie_credits(int(x))
    a,temp1=0,[]
    for i in p['cast']:
        temp={}
        if a<20:
            temp['id']=i['id']
            temp['poster_path']='https://image.tmdb.org/t/p/original'+str(i['poster_path'])
            temp['title']=i['title']
            temp['character']=i['character']
            temp1.append(temp)
        else:
            break
        a+=1
    person_ret["movies"]=temp1
    return person_ret
    

def get_movie_recom(movie_id_lst,seen_movie):
    global sk_api
    seen=[]
    for i in seen_movie:
        seen.append(i[0])
    #print(seen)
    ret_dict,temp_dict=[],{}
    for i in movie_id_lst:
        con = sqlite3.connect("app.db")
        cur = con.cursor()
        z=cur.execute("select title from movies where movieId =?",[i[0]]).fetchall()
        nta,a=0,''
        for j in z[0][0]:
            if j=='(':
                nta=1
                continue
            if j==')':
                nta=0
                continue
            if nta==0:
                a=a+j
        moviename=a.strip()
        query = sk_api+'/movieanalysis?moviename='+str(moviename)
        print(query)
        response =  requests.get(query)
        if response.status_code==200:
            array = response.json()
            for k in array:
                if k not in ret_dict:
                    temp_dict[k] = 1
                else:
                    temp_dict[k] = temp_dict[k]+1
    temp_dict=sorted(temp_dict, key=temp_dict.get, reverse=True)
    a=0
    for i in temp_dict:
        if a<10:
            z=cur.execute("select tmdb_id from movies where title like ?",[i]).fetchall()[0][0]
            if int(z) not in seen:
                print(z,seen)
                ret_dict.append((z,-1))
                a=a+1
    print(ret_dict)
    ret_dict=get_data_from_API(API_key, ret_dict)
    return ret_dict
        
    #return ret_dict
    
def get_comments(Movie_ID): #get individual movie comments from imdb
    global sk_api
    text=[]
    #must be changed according to ngrok values
    query = sk_api+'/sentimentanalyisis?id='+str(Movie_ID)
    response =  requests.get(query)
    if response.status_code==200:
        array = response.json()
        return array
    else:
        return []


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    return render_template(url_for('home.html'))
    
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        if len(email)>1 and len(password)>1:
            result = hashlib.sha256(password.encode())
            result = result.hexdigest()
            con = sqlite3.connect("app.db")
            cur = con.cursor()
            z=cur.execute("select user_id,password from user where email=?",[email]).fetchall()
            #rows = z.fetchall() 
            if z[0][1]==result:
                sess_str=rand_str()
                cur.execute("update user set sess=? where user_id=?",[sess_str,z[0][0]])
                con.commit()
                return redirect(url_for('profile',sess=sess_str))
            else :
                flash(u'Invalid Crdentials ! ','alert alert-danger alert-dismissible')
        
    return render_template('login.html')
    #return 'Hello, World!'

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        if len(email)>1 and len(password)>1 and len(name)>1:
            result = hashlib.sha256(password.encode())
            result = result.hexdigest()
            con = sqlite3.connect("app.db")
            cur = con.cursor()
            cur.execute("insert into user (name,email,password) values ( ?, ?, ?)",[str(name),str(email),str(result)]) 
            con.commit()
            flash(u'Added Account Successfully','alert alert-success alert-dismissible')
            return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/profile', methods=['GET','POST'])
def profile():
    if request.method=='GET':
        user_data=[]
        sess=request.args.get('sess')
        con = sqlite3.connect("app.db")
        cur = con.cursor()
        seen_movie=cur.execute("select movie_id,rateing from user_movie where user_id = (select user_id from user where sess= ?) order by time_stamp DESC",[sess]).fetchall()
        print(seen_movie)
        user_data.append(len(seen_movie))
        seen_movie_data=get_data_from_API(API_key, seen_movie)
        z=cur.execute("select name,email from user where user_id = (select user_id from user where sess=?)",[sess]).fetchall()
        user_data.append(z[0][0])
        user_data.append(z[0][1])
        stats=get_stats(seen_movie_data)
        popular_movie=get_popular_movies()
        z=cur.execute("select movieId from movies where tmdb_id in (select movie_id from user_movie where user_id=(select user_id from user where sess= ?))",[sess]).fetchall()
        recomended_movie=get_movie_recom(z,seen_movie)
        con.commit()
        if stats==[]:
            return render_template('profile.html',sess_str=sess,recomended_movie=recomended_movie,data=seen_movie_data,user_data=user_data,popular_movie=popular_movie)
        #print(stats[0])
        else:
            return render_template('profile.html',sess_str=sess,recomended_movie=recomended_movie,data=seen_movie_data,popular_movie=popular_movie,user_data=user_data,stats_gen=json.dumps(stats[0]),stats_rating=json.dumps(stats[1]))

@app.route('/movie', methods=['GET','POST'])
def movie():
    if request.method=='POST':
        sess=request.form['sess']
        comment=request.form['comment']
        rating=request.form['rating']
        add_to_watch=request.form['add_to_watch']
        #print(sess,comment,rating,add_to_watch)
        con = sqlite3.connect("app.db")
        cur = con.cursor()
        z=cur.execute("select user_id,movie_id from user_movie where user_id= (select user_id from user where sess=?) and movie_id = ?",[sess,add_to_watch]).fetchall()
        if z==[]:
            cur.execute("insert into user_movie (user_id,movie_id,rateing,comments) values ((select user_id from user where sess=?),?,?,?)",[sess,add_to_watch,rating,comment])
        else:
            cur.execute("update user_movie set rateing=? , comments=? where user_id = (select user_id from user where sess=?) and movie_id = ?",[rating,comment,sess,add_to_watch])
        con.commit()
        return redirect(url_for('movie',sess=sess,movie_id=add_to_watch))
    if request.method=='GET':
        user_data=[]
        sess=request.args.get('sess')
        movie_tmbd_id=request.args.get('movie_id')
        con = sqlite3.connect("app.db")
        cur = con.cursor()
        z=cur.execute("select rateing,comments from user_movie where user_id = (select user_id from user where sess= ?) and movie_id = ?",[sess,movie_tmbd_id]).fetchall()
        if z==[]:
            z.append([-1])
        seen_movie_data=get_data_from_API(API_key, [[movie_tmbd_id,z[0][0]]])
        actor=get_actor(movie_tmbd_id)
        #print(seen_movie_data[0]['imdb_id'])
        comments=get_comments(seen_movie_data[0]['imdb_id'])
        #print(comments)
        #print(seen_movie_data)
        con.commit()
        return render_template('movie.html',sess=sess,seen_movie_data=seen_movie_data[0],actor=actor,comments=comments,user_rate_comm=z)

@app.route('/actor', methods=['GET','POST'])
def actor():
    if request.method=='GET':
        sess=request.args.get('sess')
        actor_id=request.args.get('actor_id')
        actor_data=get_about_actors(actor_id)
        for i in actor_data['movies']:
            print(i)
    return render_template('actor.html',sess=sess,actor_data=actor_data)
    
    
if __name__=='__main__':
    app.run(debug=True,port=5000,use_reloader=False)
