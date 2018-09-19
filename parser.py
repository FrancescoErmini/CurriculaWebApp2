#open the csv file in read mode
import requests
import json, jsonify
from requests.auth import HTTPBasicAuth
import time

csvfile = open("course2.csv", "r") 
#skip the first line, since it contains the column headings
csvfile.readline() 
print("::::: parsing courses :::::")
course_counter = 0

# column of interest from csv
# 3 = course code | 4 = name | 5 = ssd | 6  = cfu | 0 = year | 1 = semester
for line in csvfile:
	row = line.split(";")
	course_counter += 1

	if row[4] != "PROVA FINALE " and row[4] != "LABORATORIO/TIROCINIO ":
		

		#remove last empty char from parsed strings
		id = row[3]
		id = id[:-1]
		ssd = row[5]
		ssd = ssd[:-1]
		name = row[4]
		name = name[:-1]

		payload = {
		"id": id,
		"name": name,
		"cfu": int(row[6]), 
		"ac": "2018-2019", 
		"year": int(row[0]), 
		"semester": int(row[1]), 
		"ssd": ssd, 
		"url": "url"
		};

		url = 'http://localhost:5000/course/'
		headers = {'Content-Type': 'application/json'}
		data = json.dumps(payload)
		#r = requests.options('http://localhost:5000/course/')
		print(data)

		resp = requests.post(url, data=data, auth=HTTPBasicAuth('admin', 'admin'), headers=headers)
		time.sleep(3)

#output how many we found
print("Found", course_counter, "courses")