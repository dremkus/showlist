#!/usr/bin/python

import sys
import os
import MySQLdb
from flask_mysqldb import MySQL
from htmltmpl import TemplateManager, TemplateProcessor
from flask import Flask, render_template, flash, redirect, url_for, session,  request
from wtforms import Form, StringField, TextAreaField, PasswordField, DateField, validators, IntegerField
from passlib.hash import sha256_crypt
#from shows import Calendar


app = Flask(__name__)
app.debug = True
app.secret_key='Yes, its a secr3t'

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'showdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

db = MySQL(app)

class Show:
	def __init__(self,db):
		self.session = db.connection

	def list():
		cur = self.session.cursor()
		sql = 'SELECT s.idshow,s.show_date,v.venue_name,v.venue_city,s.fee FROM showdb.showlist s join showdb.venue v on s.idvenue = v.idvenue order by s.show_date desc'
		cur.execute(sql)
		shows = cur.fechall()
		cur.close()
		return shows

@app.route('/')
def showlist():
	# Create cursor
	cur = db.connection.cursor()
	sql = 'SELECT s.idshow,s.show_date,v.venue_name,v.venue_city,s.fee FROM showdb.showlist s join showdb.venue v on s.idvenue = v.idvenue order by s.show_date desc'
	cur.execute(sql)
	shows = cur.fetchall()
	Calendar = []

	for show in shows:
		xshow = {}
		xshow["IDSHOW"] = show.get('idshow')
		xshow["SHOWDATE"] = show.get('show_date')
		xshow["VENUENAME"] = show.get('venue_name')
		xshow["VENUECITY"] = show.get('venue_city')
		xshow["FEE"] = show.get('fee')

		#
		#  Add the hash to the array
		#
		Calendar.append(xshow)
	cur.close()
	return render_template('show.html', calendar = Calendar)

@app.route('/venue')
def venuelist():
	# Create cursor
	cur = db.connection.cursor()
	sql = 'SELECT a.* FROM showdb.venue a where venue_name <> "Private Party" union SELECT b.* FROM showdb.venue b where venue_name = "Private Party"'
	cur.execute(sql)
	venuelist = cur.fetchall()
	Venues = []

	for venue in venuelist:
		xvenue = {}
		xvenue["IDVENUE"] = venue.get('idvenue')
		xvenue["VENUENAME"] = venue.get('venue_name')
		xvenue["VENUEADDRESS"] = venue.get('venue_address')
		xvenue["VENUECITY"] = venue.get('venue_city')
		xvenue["VENUEZIP"] = venue.get('venue_zip')
		xvenue["VENUEPHONE"] = venue.get('venue_phone')
		xvenue["VENUEURL"] = venue.get('venue_url')

		#
		#  Add the hash to the array
		#
		Venues.append(xvenue)
	cur.close()
	return render_template('venue.html', venues = Venues)

class ShowForm(Form):
	idvenue=IntegerField('Venue ID',[validators.DataRequired()])
	idshow = IntegerField('Show ID')
	show_date=DateField('Show Date', [validators.DataRequired()])
	show_time = StringField('Show Time')
	show_flyer_pdf = StringField('Show Flyer(PDF)')
	show_flyer_jpg = StringField('Show Flyer(JPG)')
	show_info1 = StringField('Show Info1')
	show_info2 = StringField('Show Info2')
	show_info3 = StringField('Show Info3')
	fee = IntegerField('Fee')
	action = StringField('Action')

class VenueForm(Form):
	idvenue=IntegerField('Venue ID')
	venue_name = StringField('Venue Name')
	venue_address = StringField('Venue Address')
	venue_city = StringField('Venue City')
	venue_zip = StringField('Venue Zip')
	venue_phone = StringField('Venue Phone')
	venue_url = StringField('Venue URL')

@app.route('/showadd', methods=['GET','POST'])
def showadd():
	form = ShowForm(request.form)
	form.idshow.data = 0
	form.show_time.data = '8pm'
	form.show_flyer_pdf.data = 'shows_files/<YYYYMMDD>-<VenueName>.pdf'
	form.show_flyer_jpg.data = 'images/PromoPhoto-20171028-1-bluetone.jpg'
	if request.method == 'POST' and form.validate():
		sql = "INSERT INTO showdb.showlist(idvenue,show_date,show_time,show_flyer_pdf,show_flyer_jpg,show_info1,show_info2,show_info3,fee) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		val = (int(request.form['idvenue']),
			request.form['show_date'].encode('ascii','ignore'),
			request.form['show_time'].encode('ascii','ignore'),
			request.form['show_flyer_pdf'].encode('ascii','ignore'),
			request.form['show_flyer_jpg'].encode('ascii','ignore'),
			request.form['show_info1'].encode('ascii','ignore'), 
			request.form['show_info2'].encode('ascii','ignore'),
			request.form['show_info3'].encode('ascii','ignore'),
			int(request.form['fee']))

		# Create cursor
		cur = db.connection.cursor()
		cur.execute(sql,val)
		cur.close()
		flash('Show added')
		db.connection.commit()

		return redirect('/')
	
	return render_template('showdata.html',form=form)

@app.route('/showvi/<id>', methods=['GET','POST'])
def showvi(id):
	# Create cursor
	cur = db.connection.cursor()
	sql = 'select idshow,idvenue,show_date,show_time,show_flyer_pdf,show_flyer_jpg,show_info1,show_info2,show_info3,fee from showdb.showlist where idshow=%s'%id
	cur.execute(sql)
	show = cur.fetchone()

	form = ShowForm(request.form)
	form.idvenue.data = show.get('idvenue')
	form.idshow.data = show.get('idshow')
	form.show_date.data = show.get('show_date')
	form.show_time.data = show.get('show_time')
	form.show_flyer_pdf.data = show.get('show_flyer_pdf')
	form.show_flyer_jpg.data = show.get('show_flyer_jpg')
	form.show_info1.data = show.get('show_info1')
	form.show_info2.data = show.get('show_info2')
	form.show_info3.data = show.get('show_info3')
	form.fee.data = show.get('fee')

	render_template('showdata.html',form=form,id=id)

	if request.method == 'POST' and form.validate():
		sql = "UPDATE showdb.showlist SET idvenue=%s, show_date=%s, show_time=%s, show_flyer_pdf= %s, show_flyer_jpg=%s, show_info1=%s, show_info2=%s, show_info3=%s, fee=%s where idshow=%s"
		val = (int(request.form['idvenue']),
			request.form['show_date'].encode('ascii','ignore'),
			request.form['show_time'].encode('ascii','ignore'),
			request.form['show_flyer_pdf'].encode('ascii','ignore'),
			request.form['show_flyer_jpg'].encode('ascii','ignore'),
			request.form['show_info1'].encode('ascii','ignore'), 
			request.form['show_info2'].encode('ascii','ignore'),
			request.form['show_info3'].encode('ascii','ignore'),
			int(request.form['fee']),
			int(request.form['idshow']))

		cur.execute(sql,val)
		cur.close()
		flash('Show updated')
		db.connection.commit()
		return redirect('/')
	
	return render_template('showdata.html',form=form,id=id)

@app.route('/showcp/<id>', methods=['GET','POST'])
def showcp(id):
	# Create cursor
	cur = db.connection.cursor()
	sql = 'select idshow,idvenue,show_date,show_time,show_flyer_pdf,show_flyer_jpg,show_info1,show_info2,show_info3,fee from showdb.showlist where idshow=%s'%id
	cur.execute(sql)
	show = cur.fetchone()

	form = ShowForm(request.form)
	form.idvenue.data = show.get('idvenue')
	form.idshow.data = show.get('idshow')
	form.show_date.data = show.get('show_date')
	form.show_time.data = show.get('show_time')
	form.show_flyer_pdf.data = show.get('show_flyer_pdf')
	form.show_flyer_jpg.data = show.get('show_flyer_jpg')
	form.show_info1.data = show.get('show_info1')
	form.show_info2.data = show.get('show_info2')
	form.show_info3.data = show.get('show_info3')
	form.fee.data = show.get('fee')

	render_template('showdata.html',form=form,id=id)

	if request.method == 'POST' and form.validate():
		sql = "INSERT INTO showdb.showlist(idvenue,show_date,show_time,show_flyer_pdf,show_flyer_jpg,show_info1,show_info2,show_info3,fee) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		val = (int(request.form['idvenue']),
			request.form['show_date'].encode('ascii','ignore'),
			request.form['show_time'].encode('ascii','ignore'),
			request.form['show_flyer_pdf'].encode('ascii','ignore'),
			request.form['show_flyer_jpg'].encode('ascii','ignore'),
			request.form['show_info1'].encode('ascii','ignore'), 
			request.form['show_info2'].encode('ascii','ignore'),
			request.form['show_info3'].encode('ascii','ignore'),
			int(request.form['fee']))

		cur.execute(sql,val)
		cur.close()
		flash(sql)
		flash(val)
		flash('Show copied')
		db.connection.commit()
		return redirect('/')
	
	return render_template('showdata.html',form=form,id=id)

@app.route('/venueadd', methods=['GET','POST'])
def venueadd():
	form = VenueForm(request.form)
	form.idvenue.data = 0
	if request.method == 'POST' and form.validate():
		sql = "INSERT INTO showdb.venue(venue_name,venue_address,venue_city,venue_zip,venue_phone,venue_url) VALUES(%s,%s,%s,%s,%s,%s)"
		val = (request.form['venue_name'].encode('ascii','ignore'),
			request.form['venue_address'].encode('ascii','ignore'),
			request.form['venue_city'].encode('ascii','ignore'),
			request.form['venue_zip'].encode('ascii','ignore'),
			request.form['venue_phone'].encode('ascii','ignore'),
			request.form['venue_url'].encode('ascii','ignore'))

		# Create cursor
		cur = db.connection.cursor()
		cur.execute(sql,val)
		cur.close()
		flash('Venue added')
		db.connection.commit()

		return redirect('/venue')
	
	return render_template('venuedata.html',form=form)

@app.route('/venuevi/<id>', methods=['GET','POST'])
def venuevi(id):
	# Create cursor
	cur = db.connection.cursor()
	sql = 'select * from showdb.venue where idvenue=%s'%id
	cur.execute(sql)
	show = cur.fetchone()

	form = VenueForm(request.form)
	form.idvenue.data = show.get('idvenue')
	form.venue_name.data = show.get('venue_name')
	form.venue_address.data = show.get('venue_address')
	form.venue_city.data = show.get('venue_city')
	form.venue_zip.data = show.get('venue_zip')
	form.venue_phone.data = show.get('venue_phone')
	form.venue_url.data = show.get('venue_url')

	render_template('venuedata.html',form=form,id=id)

	if request.method == 'POST' and form.validate():
		sql = "UPDATE showdb.venue SET venue_name=%s, venue_address=%s, venue_city=%s, venue_zip= %s, venue_phone=%s, venue_url=%s where idvenue=%s"
		val = (request.form['venue_name'].encode('ascii','ignore'),
			request.form['venue_address'].encode('ascii','ignore'),
			request.form['venue_city'].encode('ascii','ignore'),
			request.form['venue_zip'].encode('ascii','ignore'),
			request.form['venue_phone'].encode('ascii','ignore'),
			request.form['venue_url'].encode('ascii','ignore'),
			int(request.form['idvenue']))

		cur.execute(sql,val)
		cur.close()
		flash('Venue updated')
		db.connection.commit()
		return redirect('/venue')
	
	return render_template('venuedata.html',form=form,id=id)

@app.route('/venuecp/<id>', methods=['GET','POST'])
def venuecp(id):
	# Create cursor
	cur = db.connection.cursor()
	sql = 'select * from showdb.venue where idvenue=%s'%id
	cur.execute(sql)
	show = cur.fetchone()

	form = VenueForm(request.form)
	form.idvenue.data = 0
	form.venue_name.data = show.get('venue_name')
	form.venue_address.data = show.get('venue_address')
	form.venue_city.data = show.get('venue_city')
	form.venue_zip.data = show.get('venue_zip')
	form.venue_phone.data = show.get('venue_phone')
	form.venue_url.data = show.get('venue_url')

	render_template('venuedata.html',form=form,id=id)

	if request.method == 'POST' and form.validate():
		sql = "INSERT INTO showdb.venue(venue_name,venue_address,venue_city,venue_zip,venue_phone,venue_url) VALUES(%s,%s,%s,%s,%s,%s)"
		val = (request.form['venue_name'].encode('ascii','ignore'),
			request.form['venue_address'].encode('ascii','ignore'),
			request.form['venue_city'].encode('ascii','ignore'),
			request.form['venue_zip'].encode('ascii','ignore'),
			request.form['venue_phone'].encode('ascii','ignore'),
			request.form['venue_url'].encode('ascii','ignore'))

		cur.execute(sql,val)
		cur.close()
		flash('Venue Copied')
		db.connection.commit()
		return redirect('/venue')
	
	return render_template('venuedata.html',form=form,id=id)

if __name__ == '__main__':
    app.run() 
