from bs4 import BeautifulSoup as BS
import requests
import csv
import sys

BASEURL = "http://wbutech.net/"
EVEN = "show-result_even.php"
ODD = "show-result_odd.php"
URL = BASEURL+EVEN

headers = {}
#Add custom headers
headers['Referer'] = "http://wbutech.net/result_even.php"
headers['Origin'] = "http://wbutech.net"
headers['Host'] = "wbutech.net"
headers['User-Agent']= 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'

#Create data
data = {'semno':'6', 'rollno': '13000112122', 'rectype': '1'}

def dumpData(headers, data, url):
	try:
		dump = requests.post(url, data=data, headers=headers)
		if (dump.status_code == 200):
			parseData(dump.text)
		else:
			print "[-] Status code of "+dump.status_code+" received."
	except requests.ConnectionError as connecterror:
		print "[-] Error while connecting to server."

def parseData(dump):
	soup = BS(dump)
	tables = soup.find_all('table')

	#tables[0] -> name and roll no
	name = tables[0].find_all('th')[1].text.split(':')[1].strip()
	roll = tables[0].find_all('th')[2].text.split(':')[1].strip()

	#user is a dictionary. Keys : name, roll, marks, sgpa_even, sgpa_odd, ygpa
	user = {'name':name, 'roll':roll}

	#tables[1] -> marks
	#data : code, subject, grade, points
	marks = dict()
	code, subject, grade, points = [], [], [], []
	rows = tables[1].find_all('tr')
	for row in rows:
		cols = row.find_all('td')	
		if cols:
			code.append(cols[0].text.strip())
			subject.append(cols[1].text.strip())
			grade.append(cols[2].text.strip())
			points.append(cols[3].text.strip())
	marks['code']=code
	marks['subject']=subject
	marks['grade']=grade
	marks['points']=points
	user['marks'] = marks

	#tables[2] -> ygpa, sgpa
	sgpa_odd = tables[2].find_all('tr')[0].text.split(':')[1].strip()
	sgpa_even = tables[2].find_all('tr')[1].text.split(':')[1].strip()
	ygpa = tables[2].find_all('tr')[2].text.split(':')[1].strip()

	user['sgpa_odd'] = sgpa_odd
	user['sgpa_even'] = sgpa_even
	user['ygpa'] = ygpa

	print user

dumpData(headers, data, "http://wbutech.net/show-result_even.php")
