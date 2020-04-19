# Project overview
Simpliest email reader and sender in Python.
Let’s go through a small program to uncap the possibilities of IMAP and SMPT email protocols and Python (v3.7)

## Features:
- [x] Log in email server
- [x] Read emails from an inbox
- [x] Send emails
- [x] Log onto terminal

## Theory
First, let’s refresh our memory about the protocols.
### What is IMAP?
Internet Message Access Protocol (IMAP) is an Internet standard protocol used to retrieve email messages from a mail server (e.g. Gmail, Yahoo) over a TCP/IP connection. Created in 1986. The latest version is IMAP4 (comes from 90s!) which is supported in the imaplib with IMAP4 class that we are going to use! 🙂
### What is SMPT?
Simple Mail Transfer Protocol is a standard user-level protocol used for sending messages, usually through port 587 or 465. First created in 1982, updated in 2008.

## Goal
The goal of this exercise is to go though inbox and pick the UNANSWERED emails that were sent today. Assuming that a hard-working developer requires some holidays, we need to notify our acquaintances that we are out of the office. For that, we will use EmailSender to send series of email to each of them with specified message.
Here’s the code of the main.py achieving that.
First, we need a valid email and password.
```
email_user = "xxx@gmail.com"
password = "xxx"
```
We instantiate reader and sender, feeding them both with credentials and optionally server and ports. By default, they connect to GMAIL.
```
email_reader = ImapReader(email_user, password)
email_sender = EmailSender(email_user, password)

infos = email_reader.get_unanswered_emails(since=datetime.date.today())

body = "I am on holiday till Monday. I will answer you when I'm back in the office."
email_sender.sendEmails(body, infos)
```

With the reader I fetch all the unanswered mail from today.
```
infos = email_reader.get_unanswered_emails(since=datetime.date.today())
```
What I get is a list of dictionaries looking like this:
```
[
	{'subject': 'RE:Wednesday business meeting', 'to': '"Andrea Algeria" '},
	{'subject': 'RE:Buy more parrot food', 'to': 'dolphin@gmail.com'},
	{'subject': 'RE:New apartment to rent in Cape Town City Centre', 'to': 'agent_bill@houses.co.za'}
]
```
As you can see dolphin@gmail.com sent us a message titled Buy more parrot food. The method prepared a dictionary with 2 attributes: subject and to. We appended ‘RE:’ to the subject and we are going to send a message back to Mr. Dolphin.
With the information ready, we can now pass it to the `email_sender` together with a professionally sounding note informing everyone we are on holiday.
```
body = "I am on holiday till Monday. I will answer you when I'm back in the office."
email_sender.sendEmails(body, infos)
```

Here comes a closer look at what’s going on behind the scenes.

## Reading mail
To be able to read mail we need to:
 1. Log in with valid email address and password over valid port
 2. Select an inbox
 3. Search for emails defining optional criteria
 4. Decode the email data
 
Here’s how it’s been implemented in code:
ImapReader‘s constructor creates IMAP4_SSL object, it needs the host and port. With that object called simply imap we log in by passing in email address and password in log_in().
```
class ImapReader(Logger):
    def __init__(self, email_address, password, host="imap.gmail.com", ssl_port=993, log=True):
        Logger.log = log
        self.email_address = email_address
        self.password = password

        self.imap = IMAP4_SSL(host, ssl_port)
        self.log_in()

    def log_in(self):
        self.imap.login(self.email_address, self.password)
```
2. Inside get_unanswered_emails() we select the inbox, by default it’s the main one containing all the received mail. 
```
def get_unanswered_emails(self, since=None, inbox_name= 'INBOX'):
    self.imap.select(inbox_name)
    ...
```
We construct a query searching for emails sent since date saved in since variable. By default it’s today. A TypeError is thrown if invalid type was passed in.
```
    # Set a default value to today
    since = datetime.date.today() if since is None else since

    if not isinstance(since, datetime.date):
        raise TypeError("since parameter must be datetime.date type")
```
We construct the criteria.
```
since_formatted = since.strftime("%d-%b-%Y")
query = f"UNANSWERED SENTSINCE {since_formatted}"
status, response = self.imap.search(None, query)
If status is OK we can proceed with fetching the ids of emails embedded in response.
if status == 'OK':
	unread_msg_nums = response[0].split() # Returns bytes
else:
	return []
```
for loop is going to fetch individual emails by their ids, decode them into readable strings so we can subtract Subject and From elements 🙂 At the end all the info is returned in form of a list.
```
new_email_infos = []

for e_id in unread_msg_nums:
    rv, data = self.imap.fetch(e_id, '(RFC822)')
    decoded_string = data[0][1].decode('utf-8')
    msg = email.message_from_string(decoded_string)

    email_info = {
        "subject": "RE:" + str(msg['Subject']),
        "to": msg['From']
    }
    new_email_infos.append(email_info)

return new_email_infos
```

## Sending mail
To be able to send an email we need:
 1. Create SMTP object.
 2. Log in.
 3. Send email passing From, To and Message strings.
 
To simplify the matters, I created the SMTP_SSL object and logged into the mail service inside the constructor of EmailSender.
class EmailSender(Logger):
```
    def __init__(self, email_address="", password="", host="smtp.gmail.com", port=465, log=True):
        Logger.log = log
        self.email_address = email_address
        self.password = password

        self.server = smtplib.SMTP_SSL(host, port)
        self.server.login(self.email_address, self.password)
```

sendEmails() loops through list of email info. First it checks if the sender is the same as the receiver. We do not need any extra clutter in our mailboxes 🙂 Afterwards we construct body of the email, inject Subject into it and call sendmail().

```
def sendEmails(self, body, infos):

    for info in infos:
        if info['to'] == self.email_address: # To not reply to yourself
            continue
        try:
            body_with_subject = f"Subject: {info['subject']}\n\n{body}" # Include subject in the body
            self.server.sendmail(self.email_address, self.email_address, body_with_subject)
        except Exception as e:
            self.Log(str(e))
```
