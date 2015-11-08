from bs4 import BeautifulSoup as BS
import requests
import csv
import sys
import optparse

BASEURL = "http://wbutech.net/"
EVEN = "show-result_even.php"
ODD = "show-result_odd.php"
REVIEW = "show-review.php"

headers = {}
#Add custom headers
headers['Referer'] = "http://wbutech.net/result_even.php"
headers['Origin'] = "http://wbutech.net"
headers['Host'] = "wbutech.net"
headers['User-Agent']= 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
#Create data


def dumpData(headers, data, url, q):
	try:
		dump = requests.post(url, data=data, headers=headers)
		if (dump.status_code == 200):
			parsed = parseData(dump.text,q)
			if(parsed):
				logData(parsed,q)
		else:
			print "[-] Status code of "+dump.status_code+" received."
	except requests.ConnectionError as connecterror:
		print "[-] Error while connecting to server."

def parseData(dump,q):
	soup = BS(dump,"lxml")
	tables = soup.find_all('table')

	#tables[0] -> name and roll no
	try:
		name = tables[0].find_all('th')[1].text.split(':')[1].strip()
		roll = tables[0].find_all('th')[2].text.split(':')[1].strip()
	except IndexError:
		return False

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
	if q == "even":
		sgpa_even = tables[2].find_all('tr')[1].text.split(':')[1].strip()
		ygpa = tables[2].find_all('tr')[2].text.split(':')[1].strip()
	else:
		sgpa_even = None
		ygpa = tables[2].find_all('tr')[1].text.split(':')[1].strip()

	user['sgpa_odd'] = sgpa_odd
	user['sgpa_even'] = sgpa_even
	user['ygpa'] = ygpa
	return user

def logData(data,q):
	writer=csv.writer(sys.stdout)
	if q == "even":
		writer.writerow((data['name'], data['roll'], data['sgpa_even'], data['ygpa']))
	else:
		writer.writerow((data['name'], data['roll'], data['sgpa_odd'], data['ygpa']))

def main():
	parser = optparse.OptionParser()
	parser.add_option('-g', '--group', action="store_true", default=False, help="boolean indicating whether individual or multiple dump. Multiple dump if set.")
	parser.add_option('-s', '--semester', action="store", dest="semester", help="semester number")
	parser.add_option('-r', '--roll', action="store", dest="roll", help="roll number | starting roll number in case of multi dump")
	(options, args) = parser.parse_args();

	#Check for single or multi user
	if options.group:
		print "[+] Initialising multi dump mode."
	else:
		print "[+] Initialising single user mode."

	#Check if semester is set or not
	if options.semester:
		print "[+] Semester : ",options.semester
	else:
		try:
			options.semester = int(raw_input("Enter the semester : "))
		except KeyboardInterrupt:
			print "\nInterrupted. Not enough data to continue. Exiting."
			sys.exit(0)

	if options.roll:
		if options.group:
			print "[+] Starting roll number : ",options.roll
			try:
				limit = int(raw_input("Enter the number of students : "))
			except KeyboardInterrupt:
				print "\nInterrupted. Not enough data to continue. Exiting."
				sys.exit(0)
		else:
			print "[+] Roll number : ",options.roll
	else:
		if options.group:
			try:
				options.roll=int(raw_input("Enter starting roll number : "))
				limit = int(raw_input("Enter the number of students : "))
			except KeyboardInterrupt:
				print "\nInterrupted. Not enough data to continue. Exiting."
				sys.exit(0)	
		else:
			try:
				options.roll=int(raw_input("Enter roll number : "))
				limit = 0
			except KeyboardInterrupt:
				print "\nInterrupted. Not enough data to continue. Exiting."	
				sys.exit(0)

	if int(options.semester) % 2==0:
		q="even"
	else:
		q="odd"

	for i in range(0,limit+1):
		data = {'semno':str(options.semester), 'rollno': str(int(options.roll)+i), 'rectype': '1'}
		dumpData(headers, data, "http://wbutech.net/show-result_even.php",q)

#dumpData(headers, data, "http://wbutech.net/show-result_even.php")
main()
