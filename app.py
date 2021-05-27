from flask import Flask,redirect,url_for,render_template,request,session,flash
import os
from datetime import datetime
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from googleapiclient.discovery import build
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'keys.json', scope)
gc = gspread.authorize(credentials)
sheet=gc.open('CCproj').sheet1

fg1=''

app=Flask(__name__)
app.secret_key="project"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.permanent_session_lifetime = timedelta(minutes=5)

db=SQLAlchemy(app)

class users(db.Model):
	_id=db.Column("id",db.Integer,primary_key=True)
	name=db.Column(db.String(100))
	cname=db.Column(db.String(100))
	email=db.Column(db.String(100),unique=True)
	pwd=db.Column(db.String(100))

	def _init_(self,name,cname,email,pwd):
		self.name=name
		self.cname=cname
		self.email=email
		self.pwd=pwd


class final_data(db.Model):
	_id=db.Column("id",db.Integer,primary_key=True)
	sid=db.Column(db.String(100))
	cid=db.Column(db.String(100))
	j_pred=db.Column(db.String(100))

	def _init_(self,sid,cid,j_pred):
		self.sid=sid
		self.cid=cid
		self.j_pred=j_pred


sc=StandardScaler()
model=pickle.load(open('model1.pkl','rb'))
def gender(c):
    if c == "Male":
        c=1
    elif c == "Female":
       	c=0
    return c

def d_l(c):
   	if c == "Yes":
   		c=1
   	elif c == "No":
   		c=0
   	return c

def v_d(c):
   	if c == "Yes":
   		c=1
   	elif c == "No":
   		c=0
   	return c

def vehicleage(c):
   	if c==0:
   		c=0
   	elif c==1:
   		c=1
   	elif c==2:
   		c=2
   	return c




@app.route('/')
def login():
	#form=LoginForm()
	return render_template('index.html')

@app.route("/view")
def view():
	return render_template("view.html",values=users.query.all())


@app.route('/registeration',methods=['POST','GET'])
def registeration():
	return render_template('registeration.html')


@app.route('/inputs')
def inputs():
	return render_template('HomePage.html')

@app.route('/results',methods=['POST'])
def results():
	cusid=request.form['cid']
	c=request.form['cid']
	gen=request.form['gender']
	dl=request.form['Driving_license']
	vd=request.form['Vehical_Damage']
	va=request.form['vehicle']

	g=gender(gen)
	dri=d_l(dl)
	veh=v_d(vd)
	ve_age=vehicleage(va)

	test_df={"Gender":[g],"Driving_license":[dri],"Vehical_Damage":[veh],"vehicle_age":[ve_age]}
	new_test_df=pd.DataFrame(test_df)
	c=int(c)
	X=sc.fit_transform(new_test_df)
	prediction_ans=model.predict(X)[0]
	pred=int(prediction_ans)
	x=' '
	y=[]
	if prediction_ans==0:
		#z='No Insurance'
		x='Sorry, this person will not take the isurance'		
		y.append('no insurance')

	else:
		x='Sorry, this person will  take the insurance'
		y.append('insurance taken')
	sheet.append_row([pred,c])
	qw=str(prediction_ans)
	qw1=qw
	session['sid']=fg
	session['cid']=cusid
	session['r']=qw1

	print(session)
	res=final_data(sid=fg,cid=cusid,j_pred=qw1)
	db.session.add(res)
	db.session.commit()
	return render_template('Result.html',pred=x)


@app.route('/login_validation',methods=['POST','GET'])
def login_validation():
	global fg
	#q=request.form['pwd']
	fg=request.form['name']
	#fg1=request.form['name']
	#session['name']=user
	found_user =users.query.filter_by(email=fg).first()
	if found_user:
		#session['email']=found_user.email
		return render_template('Menu.html',fg=fg)
	else:
		return render_template('index.html')

@app.route('/add_user',methods=['POST'])
def l_valid():
	name =request.form['uname']
	email =request.form['email']
	cn =request.form['cname']
	pwd =request.form['pwd']
	print(name,email,cn,pwd)
	session['name']=name
	session['email']=email
	session['cname']=cn
	session['pwd']=pwd
	print(session)
	user=users(name=name,cname=cn,email=email,pwd=pwd)
	#found_user =users.query.filter_by(name=name).first()
	#found_user.email=email
	db.session.add(user)
	db.session.commit()
	return render_template('Menu.html',fg=email)

@app.route('/Menu',methods=['POST','GET'])
def Menu():
	return render_template('Menu.html',fg=fg)

@app.route('/predict',methods=['POST'])
def predict():
    return render_template('HomePage.html')

@app.route('/dashboard',methods=['POST'])
def dashboard():

	found_user =final_data.query.filter_by(sid=fg)
	return render_template("dashboard.html",values=final_data.query.all(),fg=fg)

@app.route('/logout',methods=['POST'])
def logout():
   flash(f"You have been logged out!")
   session.pop('user',None)
   session.pop('email',None)
   return redirect(url_for("login"))


	
if __name__=="__main__":
		app.run(debug=True)







	
