# Connect Therapy
This is an application developed between January and March 2018 for the IoPPN

## 1. Copyright
This is copyright of the IoPPN

## 2. Reused code
https://github.com/leemunroe/responsive-html-email-template

https://github.com/blueimp/jQuery-File-Upload

https://github.com/andyet/SimpleWebRTC -- The Web RTC API we used.

https://github.com/xdan/datetimepicker

### Python packages used
```
amqp==2.2.2
billiard==3.5.0.3
boto3==1.6.3
botocore==1.9.3
celery==4.1.0
certifi==2018.1.18
chardet==3.0.4
coverage==4.5.1
Django==2.0.3
django-betterforms==1.1.4
django-password-reset==1.0
django-sslserver==0.20
django-storages==1.6.5
docutils==0.14
future==0.16.0
idna==2.6
jmespath==0.9.3
kombu==4.1.0
PyJWT==1.6.0
PySocks==1.6.8
python-dateutil==2.6.1
pytz==2017.3
requests==2.18.4
s3transfer==0.1.13
six==1.11.0
twilio==6.10.4
urllib3==1.22
vine==1.1.4
```

## 3.Setup
### 3.1 Virtual Environment Setup
This was tested on a Linux / Mac OS installation, instructions may differ for Windows.

First run `python --version` and ensure the version of Python is 3.6 or higher.
if it is Python 2.x and you are sure you have installed Python 3.6+, then attempt
to run `python3 --version` if this displays Python 3.6+ then replace the commands
`python` with `python3` and `pip` with `pip3` in the following instructions.

NOTE: it appears that Python 3.6.x does not have virtualenv installed, and it
is not possible to install it on the ACE of KCL, to run the server, either run
the server on another computer, or attempt to install a portable distribution
of Python 3.6.x. It may be possible to install the server through Anaconda, but
this is unsupported.

The following commands are in bash

First clone the repository in a folder of your choice
`git clone https://github.kcl.ac.uk/k1631311/5CCS2SEG_Major.git`

Now cd into that directory
`cd 5CCS2SEG_Major`

Now create a new virtual environment
`python -m virtualenv venv`

Activate the virtual environment
`source venv/bin/activate`

NOTE: to deactivate just type `deactivate` though you don't want to do this now
ensure that you always activate the virtualenv before running the server.
to know if you are in the virtual environment, you should see `(venv)` written
before the current working directory on your terminal.

### 3.2 Requirements Installation
You should still be in the virtual environment at this point.

`pip install -r requirements.txt`

This should install the requirements

### 3.3 Configuration
#### 3.3.1 Database setup
This is not necessary for a development / test environment

The app is configured by default to use SQLite, however this would be unsuitable
for a deployed environment.

For instructions on how to change this, see the official
[Django Tutorial](https://docs.djangoproject.com/en/2.0/intro/tutorial02/#database-setup)

#### 3.3.2 AWS Setup
This IS necessary for a development / test environment

Follow the Amazon S3 Setup part of [this tutorial](https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html)
Create a folder `~/.aws`
`cd ~`
`mkdir .aws`
Then create this file in `~/.aws/credentials`
```
[default]
aws_access_key_id = INSERT KEY
aws_secret_access_key = INSERT KEY
```

#### 3.3.3 Twilio Setup
This is not necessary for a development / test environment

By default the server uses Twilio Test Keys, meaning that I won't be charged,
however this means that SMS messages are not actually sent, should you wish to
configure an account and send them, sign up at [twilio.com] and enter the real keys
in 'mysite/settings.py'

Updating these fields
```
TWILIO_PHONE_NUMBER = 'YOUR OUTGOING TWILIO PHONE NUMBER'

TWILIO_ACC_SID = 'YOUR ACCOUNT SID'

TWILIO_AUTH_TOKEN = 'YOUR AUTH TOKEN'
```

#### 3.3.4 Email Backend
This is not necessary for a development / test environment

By default we use the Console Backend for emails, this means that emails are not actually sent, but they appear in the
console log when running the server.

To update this to production settings, delete the line
`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
from `mysite/settings.py`

and replace it with this

```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Host for sending e-mail.
EMAIL_HOST = 'example.com'

# Port for sending e-mail.
EMAIL_PORT = 1025

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
```
Updating the fields as appropriate

#### 3.3.5 Email Reminders
This is not necessary for a development / test environment

To send email and sms reminders, you must add a cron job to call daily, at 9am,
reminders.sh.

You can do this by calling `crontab -e`
Then add a line
`0 9 * * * /home/path/to/this/repo/reminders.sh`

#### 3.3.6 WebRTC Server Setup
This is not necessary for a development / test environment

Currently the server uses a development server for WebRTC video chat, you must
change this in production. To do this set up a [signal master](https://github.com/andyet/signalmaster)
server, then add a line to `connect_therapy/static/connect_therapy/chat_view_js/webrtc.js`,
you'll find the constructor at the top of the file
```
var webrtc = new SimpleWebRTC({
    // the id/element dom element that will hold "our" video
    localVideoEl: 'localVideo',
    // the id/element dom element that will hold remote videos
    remoteVideosEl: 'remotesVideos',
    // immediately ask for camera access
    autoRequestMedia: true
});
```
Update this adding a url pointing to your signal master server
```
var webrtc = new SimpleWebRTC({
    // the id/element dom element that will hold "our" video
    localVideoEl: 'localVideo',
    // the id/element dom element that will hold remote videos
    remoteVideosEl: 'remotesVideos',
    // immediately ask for camera access
    autoRequestMedia: true,
    url: 'http://example.com'
});
```

### 3.4 Migrating the database
Now run
`python manage.py migrate`
to create the database

### 3.5 Running the tests
`python manage.py test`

To test with coverage
`coverage run --source='.' manage.py test`
Then run
`coverage html`
A HTML report will appear in the htmlcov subdirectory

### 3.6 Running the server

`python manage.py runsslserver`

Then go to https://localhost:8000
