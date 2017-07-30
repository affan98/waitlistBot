import time
import getopt
import sys
import string
from urllib.request import Request, urlopen
from twilio.rest import TwilioRestClient

accountSID = "" #REPLACE THIS

authToken = "" #REPLACE THIS

myNumber = "" #REPLACE THIS

twilioNumber = ""  #REPLACE THIS

#to find the location of each section
waitlistHTML = "<spanclass=\"section-id\">"
seatHTML = "<spanclass=\"open-seats-count\">"


secondsInADay = 86400

classToCheck = ''
sections = {}
timecheck = False

#Parse command line arguments
try:
	opts, args = getopt.getopt(sys.argv[1:],"tc:s:")
except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

for o, a in opts:
	
	if o == '-c':
		classToCheck = a
	elif o == '-s':
		for sect in a.split():
			sections[sect] = 1
	elif o == '-t':
		timecheck = True
	else:
		assert False,  'Unhandled Option'

#search query for the class
siteURL = "https://ntst.umd.edu/soc/search?courseId=" + classToCheck + "&sectionId=&termId=201708&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_faceto" + \
          "face=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&" + \
          "_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"

#function to use twilio API to send text message
def textMyself(message):
	twilioCli = TwilioRestClient(accountSID, authToken)
	twilioCli.messages.create(body=message, from_=twilioNumber, to=myNumber)


#used for 24hr checkin
currentTime = time.mktime(time.gmtime())
checkTime = currentTime + secondsInADay

while True:

	currentTime = time.mktime(time.gmtime())

	req = Request(siteURL, headers={'User-Agent': 'Mozilla/5.0'})

	#Gets the HTML from the UMD schedule of classes and removes white space
	with urlopen(req) as response:
		siteHTML = response.read()
		encoding = response.headers.get_content_charset('utf-8')
		siteHTML = siteHTML.decode(encoding)
		siteHTML = ''.join(siteHTML.split())

	
	#updates the dictionary with the correct number of seats for each section
	for key in sections:
		sectionHTML = waitlistHTML + key
		location = siteHTML.find(sectionHTML)
		location = location + siteHTML[location:].find(seatHTML)
		location += len(seatHTML)
		
		try:
			numberOfSeats = int(siteHTML[location])
		except ValueError:
			continue
		finally:
			siteHTML = siteHTML[location:]


		sections[key] = numberOfSeats

	#If a section has an open seat then send a message
	for key in sections:
		if sections[key] != 0:
			textMyself("A seat has opened up for "+ classToCheck + ' ' + key +". Get it quick!")
			time.sleep(540) # wait 10 minutes so this doesnt keep sending you texts non stop

	if timecheck and currentTime >= checkTime:
		checkTime = currentTime + secondsInADay
		textMyself("The waitlist bot is still running")


	#No need to check every second so instead check every minute
	time.sleep(60)
