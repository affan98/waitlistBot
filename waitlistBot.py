# Dependencies
import time, getopt, sys, string, re, datetime, daemon
from urllib.request import Request, urlopen
from twilio.rest import TwilioRestClient

try: # For Twilio auth
    from credentials import accountSID, authToken, myNumber, twilioNumber
except ImportError:
    raise IOError("You must include a credentials.py file with the following fields: accountSID, authToken, myNumber, and twilioNumber. See README.")

# To find the location of each section
waitlistHTML = '<spanclass=\"section-id\">'
seatHTML = '<spanclass=\"open-seats-count\">'

secondsInADay = 86400

sections = {}
sectionOrder = []


# Function to use twilio API to send text message
def textMyself(message):
    twilioCli = TwilioRestClient(accountSID, authToken)
    twilioCli.messages.create(body=message, from_=twilioNumber,
                              to=myNumber)

# Function to get the second paramater for the url
def getTerm(customSemester, season, year):
    now = datetime.datetime.now()
    #custom semester can take any semester
    if customSemester:
    	if season == 'SPRING':
    		seasonNum = '01'
    	elif season == 'SUMMER':
    		seasonNum = '05'
    	elif season == 'FALL':
    		seasonNum = '08'
    	else:
    		seasonNum = '12'

    #otherwise default to either spring or fall
    else:
    	year = str(now.year)
    	month = now.month
        #if month is between february and september then we want to check for fall of this year
    	if month >= 2 and month <= 9:
    		seasonNum = '08'
    	else:
        #otherwise we check for spring.
            seasonNum = '01'
            if month != 1:
                year = str(now.year + 1)

    return year + seasonNum

# Checks if seat has opened up for a class
def checkSeats(url, classToCheck):

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    # Gets the HTML from the UMD schedule of classes and removes white space
    with urlopen(req) as response:
        siteHTML = response.read()
        encoding = response.headers.get_content_charset('utf-8')
        siteHTML = siteHTML.decode(encoding)
        siteHTML = "".join(siteHTML.split())

    # If a section has an open seat then send a message
    sortedSections = sorted(sectionOrder)

    # Updates the dictionary with the correct number of seats for each section
    for key in sortedSections:
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

    for key in sortedSections:
        #print(key, sections[key])
        if sections[key] != 0:
            #print("A seat has opened up for {} {}. Get it quick!".format(classToCheck, key))
            textMyself("A seat has opened up for {} {}. Get it quick!".format(classToCheck, key))
            sys.exit()


def main():

    classToCheck = ""
    season = ""
    year = ""

    # Parse command line arguments
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'tc:s:p:')
    except (getopt.GetoptError, err):
        # Print help information and exit:
        print(err)  # Will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    checkClass = False
    checkSection = False
    customSemester = False
    timecheck = False

    for (o, a) in opts:
        if o == '-c':
            checkClass = True
            classToCheck = a
        elif o == '-s':
            checkSection = True
            for sect in a.split():
                sectionOrder.append(sect)
                sections[sect] = 1
        elif o == '-t':
            timecheck = True
        elif o == '-p':
            customSemester = True
            match = re.search('(\w{4,6})(\d{4})',a)
            season = match.group(1).upper()
            year = match.group(2)


        else:
            assert False, "Unhandled Option"

    if not checkClass or not checkSection:
        print("You must specify both a class(-c) and class sections(-s). sections must be input as there 4 digit codes seperated by spaces")
        sys.exit(2)

    
    term = getTerm(customSemester, season, year)

    # Search query for the class
    SITE_URL = "https://ntst.umd.edu/soc/search?courseId={}&sectionId=&termId={}&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on".format(classToCheck, term)
    # Used for 24hr checkin
    currentTime = time.mktime(time.gmtime())
    checkTime = currentTime + secondsInADay
    
    while True:
        checkSeats(SITE_URL, classToCheck)

        currentTime = time.mktime(time.gmtime())

        if timecheck and currentTime >= checkTime:
            checkTime = currentTime + secondsInADay
            textMyself("The waitlist bot is still running")

        # No need to check every second so instead check every minute
        time.sleep(60)


with daemon.DaemonContext():
    main()