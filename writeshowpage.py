#!/usr/bin/python2

import jinja2
import sys
import os
import MySQLdb

if len(sys.argv) > 1 :
    script, argpath = sys.argv
    os.chdir(argpath)
else:
    argpath = "."
outfile = argpath  + "/shows.html"
dbhost = 'localhost'
dbuser = 'root'
dbpswd = '40ounce'
dbname = 'showdb'

#  template directory and file for Jinja2 processing
templateDir = "/var/www/showlist/templates"
TEMPLATE_FILE="shows.html"

#
#  Connect to the database
#
db = MySQLdb.connect(dbhost,dbuser,dbpswd,dbname)

#
#  Create a cursor to hold the query results
#
cursor = db.cursor()
query = "SELECT dy, show_flyer_pdf, show_flyer_jpg, show_dt, venue_name, venue_address, venue_city, venue_zip, venue_phone, venue_url, show_time, show_info1, show_info2, show_info3 FROM show_v WHERE show_date >= curdate() order by show_date asc"

#
#  Execute the query
#
cursor.execute(query)
#
#  Create an empty array to hold the calendar entries
#
Calendar = []
#
#  Parse the rows into a hash and load each hash into the calendar array
#
for (dy, show_flyer_pdf, show_flyer_jpg, show_dt, venue_name, venue_address, venue_city, venue_zip, venue_phone, venue_url, show_time, show_info1, show_info2, show_info3 ) in cursor:
	#
	#  If this is the first row, capture the next flyer
	#
	try:
		flyer
	except NameError:
		flyer = show_flyer_jpg

	#
	#  Create a new hash for each calendar entry
	#
	show = {}
	show["SHOWDAY"] = dy
	show["SHOWPDF"] = show_flyer_pdf
	show["SHOWJPG"] = show_flyer_jpg
	show["SHOWDATE"] = show_dt
	show["VENUENAME"] = venue_name
	show["VENUEADDR"] = venue_address
	show["VENUECITY"] = venue_city
	show["VENUEZIP"] = venue_zip
	show["VENUEPHONE"] = venue_phone
	show["VENUEURL"] = venue_url
	show["STARTTIME"] = show_time
	show["SHOW_INFO1"] = show_info1
	show["SHOW_INFO2"] = show_info3
	show["SHOW_INFO3"] = show_info2

	#
	#  Add the hash to the array
	#
	Calendar.append(show)

#
#  Process the Jinja2 template
templateLoader = jinja2.FileSystemLoader(searchpath=templateDir)
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template(TEMPLATE_FILE)

outText = template.render(flyer=flyer,show="",calendar=Calendar)

#print(outText)
#
#  Write the output
#
f = open(outfile,'w')
f.write(outText)
f.close()

