# Dependencies
import time
import getopt
import sys
import string
from urllib.request import Request, urlopen
from twilio.rest import TwilioRestClient
try: # For Twilio auth
    from credentials import accountSID, authToken, myNumber, twilioNumber
except ImportError:
    raise IOError("You must include a credentials.py file with the following fields: accountSID, authToken, myNumber, and twilioNumber. See README.")

# To find the location of each section
waitlistHTML = '<spanclass="section-id">'
seatHTML = '<spanclass="open-seats-count">'

secondsInADay = 86400

classToCheck = ""
sections = {}
timecheck = False

# Parse command line arguments
try:
    (opts, args) = getopt.getopt(sys.argv[1:], 'tc:s:')
except getopt.GetoptError, err:
    # Print help information and exit:
    print err  # Will print something like "option -a not recognized"
    usage()
    sys.exit(2)

checkClass = False
checkSection = False

for (o, a) in opts:
    if o == '-c':
        checkClass = True
        classToCheck = a
    elif o == '-s':
        checkSection = True
        for sect in a.split():
            sections[sect] = 1
    elif o == '-t':
        timecheck = True
    else:
        assert False, "Unhandled Option"

if not checkClass or not checkSection:
    print "You must specify both a class(-c) and class sections(-s). sections must be input as there 4 digit codes seperated by spaces"
    sys.exit(2)

# Search query for the class
SITE_URL = "https://ntst.umd.edu/soc/search?courseId={}&sectionId=&termId=201708&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on".format(classToCheck)


# Function to use twilio API to send text message
def textMyself(message):
    twilioCli = TwilioRestClient(accountSID, authToken)
    twilioCli.messages.create(body=message, from_=twilioNumber,
                              to=myNumber)


# Used for 24hr checkin
currentTime = time.mktime(time.gmtime())
checkTime = currentTime + secondsInADay

def main():
    currentTime = time.mktime(time.gmtime())

    req = Request(SITE_URL, headers={'User-Agent': 'Mozilla/5.0'})

    # Gets the HTML from the UMD schedule of classes and removes white space

    with urlopen(req) as response:
        siteHTML = response.read()
        encoding = response.headers.get_content_charset('utf-8')
        siteHTML = siteHTML.decode(encoding)
        siteHTML = "".join(siteHTML.split())

    # Updates the dictionary with the correct number of seats for each section

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

    # If a section has an open seat then send a message

    for key in sections:
        if sections[key] != 0:
            textMyself("A seat has opened up for {} {}. Get it quick!".format(classToCheck, key))
            time.sleep(540)  # Wait 10 minutes so this doesnt keep sending you texts non stop

    if timecheck and currentTime >= checkTime:
        checkTime = currentTime + secondsInADay
        textMyself("The waitlist bot is still running")

# Run main loop
while True:
    main()

    # No need to check every second so instead check every minute
    time.sleep(60)
