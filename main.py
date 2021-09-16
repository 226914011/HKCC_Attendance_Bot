import os
try:
	import requests #import lib
except ImportError:
	print("Trying to Install required module: requests\n")
	os.system('python -m pip install requests')
	import requests

try:
	import bs4 #import lib
except ImportError:
	print("Trying to Install required module: bs4\n")
	os.system('python -m pip install bs4')
	import bs4


from secret import username, password #import username and password

#User Ac default check
if username == "XXXXXXXXA" or password == "XXXXXXXXX":
	print("Please replace your username and password first.")
	exit(1)

#Print Current time
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

def checking(a):
	if a == 502:
		print("Access Denied or Server Broke Down")
		exit(1)

#Preconfig
headers = {
    'User-Agent': 'User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
}

############################################################################################################################################################
#Login

url ='https://moodle.cpce-polyu.edu.hk/calendar/view.php?view=day'
session = requests.Session()

#get MoodleSessioncpcemoodle3
response = session.get(url=url,headers = headers, allow_redirects=False)
print(response.status_code)
checking(response.status_code)

#get with MoodleSessioncpcemoodle3
MoodleSessioncpcemoodle3 = response.cookies.get_dict()

response = session.get(url='https://moodle.cpce-polyu.edu.hk/auth/saml/index.php',headers = headers, cookies = MoodleSessioncpcemoodle3,allow_redirects=False)
print(response.status_code)
checking(response.status_code)
PHPSESSID = response.cookies.get_dict()
data= response.text

soup=bs4.BeautifulSoup(data, "html.parser")
href=soup.find(id="redirlink")

ncookie = {**MoodleSessioncpcemoodle3, **PHPSESSID}
response = session.get(url = href.get('href'),headers = headers,cookies = ncookie,allow_redirects=False)
data=response.text

soup=bs4.BeautifulSoup(data, "html.parser")

#find data
LASTFOCUS = soup.find(id="__LASTFOCUS")
VIEWSTATE = soup.find(id="__VIEWSTATE")
VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")
EVENTTARGET = soup.find(id="__EVENTTARGET")
EVENTVALIDATION = soup.find(id="__EVENTVALIDATION")
SAMLRequest = soup.find(id="aspnetForm")
SAMLRequest.get('value')


data = {
	"__LASTFOCUS": LASTFOCUS.get('value'),
	"__VIEWSTATE": VIEWSTATE.get('value'),
	"__VIEWSTATEGENERATOR": VIEWSTATEGENERATOR.get('value'),
	"__EVENTTARGET": EVENTTARGET.get('value'),
	"__EVENTVALIDATION": EVENTVALIDATION.get('value'),
	"__db": "15",
	"ctl00$ContentPlaceHolder1$UsernameTextBox": username,
	"ctl00$ContentPlaceHolder1$PasswordTextBox": password,
	"ctl00$ContentPlaceHolder1$SubmitButton": "Sign+In",
	"ctl00$ContentPlaceHolder1$UserAccountControlWSText": "",
	"ctl00$ContentPlaceHolder1$UserUPNWSText": "",
	"ctl00$ContentPlaceHolder1$ADFSDevVersion": "1.1.6862.25998"
}

#Post the Ac Info
result = session.post(url="https://adfs.cpce-polyu.edu.hk/"+ SAMLRequest.get('action'),headers = headers,data=data,allow_redirects=False)

#Get the MSISAuthenticated,MSISLoopDetectionCookie,SamlSession
cdict = result.cookies.get_dict()

result2 = session.post(url="https://adfs.cpce-polyu.edu.hk/"+ SAMLRequest.get('action'),headers = headers,cookies = cdict,allow_redirects=False)
print(result2.status_code)
checking(result2.status_code)

data= result2.text
soup=bs4.BeautifulSoup(data, "html.parser")
SAMLResponse = soup.find("input",{"name":"SAMLResponse"})
RelayState = soup.find("input",{"name":"RelayState"})

#User Ac Validation Check
if SAMLResponse is None:
	print("Username or password invalid,please try agin.")
	print()
	exit(1)

data = {
	"SAMLResponse": SAMLResponse.get('value'),
	"RelayState": RelayState.get('value'),
}

result3 = requests.post(url= 'https://moodle.cpce-polyu.edu.hk/simplesaml/module.php/saml/sp/saml2-acs.php/moodlesso', cookies=ncookie,data = data,allow_redirects=False)
print(result3.status_code)
checking(result3.status_code)

#merge required cookies
cookie = {**ncookie, **result3.cookies.get_dict()}
result4 = requests.post(url= 'https://moodle.cpce-polyu.edu.hk/auth/saml/index.php', cookies=cookie,allow_redirects=False)
print(result4.status_code)
checking(result4.status_code)

cjdict = result4.cookies.get_dict()

result5 = requests.post(url= 'https://moodle.cpce-polyu.edu.hk', cookies=cjdict)
print(result5.status_code) 
checking(result5.status_code)

if result5.status_code == 200:
	print("Login successful!")
	print()
else:
	print("Login unsuccessful!")
	print()
	exit(1)

############################################################################################################################################################
#Get attendance

result6 = requests.post(url= 'https://moodle.cpce-polyu.edu.hk/calendar/view.php?view=day', cookies=cjdict)

print(result6.status_code)

data = result6.text
soup=bs4.BeautifulSoup(data, "html.parser")

events = soup.find_all("div",{"class":"event"})

if events == None:
	print("No event yet!")
	exit(1)

attendance = []

for tag in events:
	if tag.find("span",{"class":"dimmed_text"}) == None:
		if tag.find("div",{"class":"description card-block calendar_event_attendance"}) != None:
			attendances = tag.find("div",{"class":"description card-block calendar_event_attendance"})
			attendance.append(attendances.find('a', href=True)['href'])
		print("Not attendence")
	else:
		print("Dimmed Message")

print()

if not attendance:
	print("The attendances list is empty!")
	print()
	exit(1)
else:
	print(attendance)
	print()

result7 = requests.post(url= attendance[0], cookies=cjdict)
print(result7.status_code)


############################################################################################################################################################
#Submit attendence

data = result7.text
soup=bs4.BeautifulSoup(data, "html.parser")
submit = soup.find("td",{"class":"statuscol cell c2 lastcol"})

if submit == None:
	print("No attendance yet!")
	exit(1)

url = submit.find('a', href=True)['href']
sessid = url.split("?")[1].split("&")[0].split("=")[1]
sesskey = url.split("?")[1].split("&")[1].split("=")[1]

result8 = requests.post(url= url, cookies=cjdict)
print(result8.status_code)

data = result8.text
soup=bs4.BeautifulSoup(data, "html.parser")
status = soup.find("input",{"type":"radio"},{"name":"status"},)
#{"class":"form-check-input "},

data = {
	"sessid": sessid,
	"sesskey": sesskey,
	"_qf__mod_attendance_student_attendance_form": "1",
	"mform_isexpanded_id_session": "1",
	"status": status.get('value'),
	"submitbutton": "Save+changes",
}


result9 = requests.post(url= 'https://moodle.cpce-polyu.edu.hk/mod/attendance/attendance.php', cookies=cjdict,data=data,allow_redirects=False)

print(result9.status_code)
print()
#print(result9.headers)
print(result8.url)
print()

if result5.status_code == 200:
	print("Take attendance successful!")
	print()
	exit(0)
else:
	print("Take attendance unsuccessful!")
	print()
	exit(1)