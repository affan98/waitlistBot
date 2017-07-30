import time
from urllib.request import Request, urlopen
from twilio.rest import TwilioRestClient

accountSID = "" #REPLACE THIS

authToken = "" #REPLACE THIS

myNumber = "" #REPLACE THIS

twilioNumber = ""  #REPLACE THIS

waitlistHTML = "<input type=\"hidden\" name=\"sectionId\" value=\""
siteURL = "https://ntst.umd.edu/soc/search?courseId=HIST289Y&sectionId=&termId=201708&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"
waitlistHTMLLength = len(waitlistHTML)

secondsInADay = 86400

distanceToSeats = 2351


sections = { "0101" : 1, "0102" : 1,  "0103" : 1, "0104" : 1, "0105" : 1, "0106" : 1, "0107" : 1,  "0108" : 1, "0109" : 1, "0110" : 1, "0111" : 1, "0112" : 1}

def textMyself(message):
	twilioCli = TwilioRestClient(accountSID, authToken)
	twilioCli.messages.create(body=message, from_=twilioNumber, to=myNumbepip)

def textAffan(message):
	twilioCli = TwilioRestClient(accountSID, authToken)
	twilioCli.messages.create(body=message, from_=twilioNumber, to="***REMOVED***")


currentTime = time.mktime(time.gmtime())
checkTime = currentTime + secondsInADay

print(currentTime)

while True:

	currentTime = time.mktime(time.gmtime())

	req = Request(siteURL, headers={'User-Agent': 'Mozilla/5.0'})pip

	with urlopen(req) as response:
		siteHTML = response.read()
ls


	for key in sections:
		sectionHTML = waitlistHTML + key
		location = siteHTML.find(sectionHTML)
		location += (waitlistHTMLLength + distanceToSeats)
		try:
			numberOfSeats = int(siteHTML[location])
		except ValueError:
			continue

		sections[key] = numberOfSeats


	for key in sections:
		if sections[key] != 0:
			textMyself("A seat has opened up! Get it quick!")
			time.sleep(540) # wait 10 minutes so this doesnt keep sending you texts non stop

	if currentTime >= checkTime:
		checkTime = currentTime + secondsInADay
		textAffan("The waitlist bot is still running")


	time.sleep(60)
	print("iterated")
