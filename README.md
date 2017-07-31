# UMD Waitlist Skipper
--------------------
### Description
This script will monitor the UMD Schedule of classes and text you when a seat opens up.

### Set up
Get a free Twilio account at https://www.twilio.com/try-twilio

Create a file called `credentials.py` and include your account SID, auth token, Twilio number (you get one free as part of your account), and the number at which you want to receive notifications.

`credentials.py`
```Python
Account_SID = "Your SID here"
Auth_TOKEN = "Your Auth token here"
myTwilioNumber = "copy paste your number"
myNumber = "use this format +15556665555"
```

Before running, make sure to install the Twilio module.

```
$ pip install twilio
```

### Usage

To run the script you must specify a class name and which sections you want to check.

```
$ python3 waitlistBot.py -c "MATH241" -s "0101 0201 0405"
```

To run the script in the background:
```
$ nohup python3 waitlistBot.py -c "MATH241" -s "0101 0201 0405" &
```
To get this to work properly the machine should always be on.

I suggest using a remote machine such as an AWS EC2 instance.
