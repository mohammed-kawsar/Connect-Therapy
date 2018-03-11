# Connect Therapy
This is an application developed between January and March 2018 for the IoPPN

## Copyright
This is copyright of the IoPPN

## Reused code
https://github.com/leemunroe/responsive-html-email-template

https://github.com/blueimp/jQuery-File-Upload

https://github.com/andyet/SimpleWebRTC -- The Web RTC API we used.

## Setup
You MUST set up `python manage.py reminders` to run at 9am every day using
`at` on Windows, or `cron` on UNIX-like operating systems

You must change the twilio keys in settings.py they are test keys

### AWS
You MUST also add the following:

```[default]```

```aws_access_key_id = AKIAI2LWWJECKZ6F56YA```

```aws_secret_access_key = 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```

to ~/.aws/credentials

Note: The above are temporary AWS Keys and will be changed.
