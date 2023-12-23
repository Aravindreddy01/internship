from ast import Num
from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from numpy import number
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail, Message
import os

import json

with open('config.json','r') as c:
    params=json.load(c)["params"]


local_server=True
app = Flask(__name__)
app.secret_key='aravind01'



app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)


login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/recruitment'
db=SQLAlchemy(app)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))


class Registration(db.Model):
    Rid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    number = db.Column(db.String(12))
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration',methods=['POST','GET'])
@login_required
def registration():
    dept = Registration.query.all()
    if request.method == "POST":
        name=request.form.get('name')
        email=request.form.get('email')
        number=request.form.get('num')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        

        # query=db.engine(f"INSERT INTO `registration` (`name`,`email`,`number`) VALUES ('{name}','{email}','{number}')")

        # send_email_to_admin(name, email, number)
        query = Registration(name=name,email=email,number=number)
        db.session.add(query)
        db.session.commit()

        mail.send_message('GG-REC', sender=params['gmail-user'], recipients=['keerthip.cs20@rvce.edu.in'],body=f"YOUR bOOKING IS CONFIRMED THANKS FOR CHOOSING US \nYour Entered Details are :\nName: {name}\nemail: {email}\nNumber: {number}")

        
        flash("Registration Succesfull","success")
        return render_template('Registration.html')
    
    return render_template('Registration.html')

@app.route('/Signup',methods=['POST','GET'])
def Signup():
    dept = User.query.all()
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        # new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

        query = User(username=username,email=email,password=encpassword)
        db.session.add(query)
        db.session.commit()
        
        flash("Signup Succes Please Login","success")
        return render_template('login.html')

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('registration'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



app.run(debug=True)