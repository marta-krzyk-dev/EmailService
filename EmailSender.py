import smtplib
from EmailReadSend.logger import Logger


# This class enables one to send emails from one chosen address set in constructor
# Connect to GMAIL by default
class EmailSender(Logger):
    def __init__(self, email_address="", password="", host="smtp.gmail.com", port=465, log=True):
        Logger.log = log
        self.email_address = email_address
        self.password = password

        self.server = smtplib.SMTP_SSL(host, port)
        self.server.login(self.email_address, self.password)

    def sendEmails(self, body, infos):
        sent = 0

        for info in infos:
            if info['to'] == self.email_address: # To not reply to yourself
                continue

            try:
                body_with_subject = f"Subject: {info['subject']}\n\n{body}" # Include subject in the body
                self.server.sendmail(self.email_address, self.email_address, body_with_subject)
                self.Log(f"Email sent to {info['to']}\nMessage:\n{body[:200]}{'' if len(body) < 201 else '...'}")
                sent += 1
            except Exception as e:
                self.Log(str(e))

        self.Log(f"EmailSender sent {sent} email{'' if sent == 1 else 's'}.")

    def __del__(self):
        self.server.quit()
        self.Log("EmailSender closed SMTP connection")