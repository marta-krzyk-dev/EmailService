from EmailReadSend.ImapReader import ImapReader
from EmailReadSend.EmailSender import EmailSender
import datetime

email_user = "xxx@gmail.com" # Your gmail address here
password = "xxx" # Your password

# Ensure "Less sure app access" option is enabled for your mail
email_reader = ImapReader(email_user, password)
email_sender = EmailSender(email_user, password)

# Get info about emails sent today that remain UNANSWERED
infos = email_reader.get_unanswered_emails(since=datetime.date.today())

# Construct message to be sent to all as a reply
body = "I am on holiday till Monday. I will answer you when I'm back in the office."
# Answer all fetched emails with the same message
email_sender.sendEmails(body, infos)

# Free memory (optional)
del email_reader
del email_sender
