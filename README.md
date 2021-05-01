# CoWinNotify

## Prerequisites

```bash
1. Python 3.7
2. Gmail Account
3. Internet Connection (XD)
```

Go to https://myaccount.google.com/lesssecureapps and enable it. This will help the program to send email notfication. 

##How to Configure

1. Clone the repo
2. Install python packaged from requirements.txt.  
 `pip install -r requirements.txt` 
3. Add necessary configuration in the `configuration.ini` file.
```bash
[mail]
username = <gmail_id>
password = "<password_base64_encoded>"
sender = <sender_gmail_id>
receivers = <receiver_mail_id>

[cowin]
#There are two age groups 18 and 45
min_age = 18
#Notify whenever total vaccines are greater than min_capacity
min_capacity = 0 

[cron]
#Every "freq" minute, send a notification
freq = 10 

```

## How to run

### Linux/MAC
1. Search Using PinCode
```bash
nohup <directory>/CoWinNotify/src/mail.py "<pincode>" &
```
2. Search using State and District
```bash
nohup <directory>/CoWinNotify/src/mail.py "<state>" "<district>" &
```

### Windows
Refer the following article to run a python process in backgroud.
[Background Process in windows](https://www.geeksforgeeks.org/running-python-program-in-the-background/)


## How to debug

Please add necessary logging if required and monitor `app.log`.

## Possible Errors
1. SMTP Error: username and password cannot be authenticated
`Please refer ` 