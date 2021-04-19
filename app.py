from flask import Flask, flash, redirect, render_template,request, url_for
import hashlib
import sqlite3
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET','POST'])
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
                return render_template('ssn.html')
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


if __name__=='__main__':
    app.run(debug=True,port=5000,use_reloader=False)
