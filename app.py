from flask import Flask, flash, redirect, render_template, request, url_for
import requests
import hashlib
import sqlite3
import random
import string
import json

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
    for i in data:
        #print(i[3])
        # 3 for genere if get data changed please change it too
        gen=i[3].split(';')
        for j in gen:
            if j!='':
                if j not in gen_dict:
                    gen_dict[j] = 1
                else:
                    gen_dict[j] += 1

        # 9 for user rating if get data changed please change it too
        rate=i[9]
        if rate=='':
            rate_dict[0]=rate_dict[0]+1
        else:
            rate_dict[rate]=rate_dict[rate]+1
            
    ret=[conv_dict_prec(gen_dict),conv_dict_prec(rate_dict)]
    #print(ret)
    return ret

def get_data_from_API(API_key, Movie_IDs):
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
        service_req=['title','id','imdb_id','genres','poster_path','popularity','release_date','vote_average','vote_count']
        lst=[]
        for req_service in service_req:
            if text[i][req_service] is None:
                if req_service=='poster_path':
                    lst.append('https://www.sundialhome.com/assets/images/noImage.jpg')
                else:
                    lst.append(' ')
            elif req_service=='genres':
                gen=''
                for gen_name in text[i]['genres']:
                    gen=gen_name['name']+';'+gen
                lst.append(gen)
            elif req_service=='poster_path':
                lst.append(str(posterpath+text[i]['poster_path']))
            else:
                lst.append(text[i][req_service])
        lst.append(user_review[i])
        data.append(lst)
            
    return data

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
        z=cur.execute("select movie_id,rateing from user_movie where user_id = (select user_id from user where sess= ?) order by time_stamp DESC",[sess]).fetchall()
        user_data.append(len(z))
        seen_movie_data=get_data_from_API(API_key, z)
        z=cur.execute("select name,email from user where user_id = (select user_id from user where sess=?)",[sess]).fetchall()
        user_data.append(z[0][0])
        user_data.append(z[0][1])
        stats=get_stats(seen_movie_data)
        #print(stats)
        con.commit()
    return render_template('profile.html',sess_str=sess,data=seen_movie_data,user_data=user_data,stats_gen=json.dumps(stats[0]),stats_rating=json.dumps(stats[1]))

if __name__=='__main__':
    app.run(debug=True,port=5000,use_reloader=False)
