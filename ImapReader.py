from imaplib import IMAP4_SSL
import email, datetime
from EmailReadSend.logger import Logger


# ImapReader enables to log in to email server and go through inbox
# The default parameters are set to connect to GMAIL
class ImapReader(Logger):
    def __init__(self, email_address, password, host="imap.gmail.com", ssl_port=993, log=True):
        Logger.log = log
        self.email_address = email_address
        self.password = password

        self.imap = IMAP4_SSL(host, ssl_port)
        self.log_in()

    # Destructor logs out user and closes connection
    def __del__(self):
        self.imap.close()
        self.imap.logout()
        self.Log("ImapReader closed IMAP connection")

    def log_in(self):
        self.Log("ImapLogger logging in...")
        self.imap.login(self.email_address, self.password)
        # self.imap.check()
        # # In order to use with Gmail, you have to turn on "Less secure app access" in settings

    # Searches for all unaswered emails since a given date
    # Returns a list of dictionaries:
    # {
    #      "subject": <string>,
    #      "to": <string>
    # }
    def get_unanswered_emails(self, since=None, inbox_name= 'INBOX'):

        self.Log("ImapLogger reading emails...")

        # Login to INBOX
        self.imap.select(inbox_name)

        # Set a default value to today
        since = datetime.date.today() if since is None else since

        if not isinstance(since, datetime.date):
            raise TypeError("since parameter must be datetime.date type")

        since_formatted = since.strftime("%d-%b-%Y")
        self.Log(type(since))
        query = f"UNANSWERED SENTSINCE {since_formatted}"

        self.Log(f"ImapLogger executing search query \"{since_formatted}\"")

        status, response = self.imap.search(None, query)

        if status == 'OK':
            unread_msg_nums = response[0].split()  # Returns bytes
            self.Log(f"ImapLogger executing search found {len(unread_msg_nums)} messages.")
        else:
            self.Log(f"ImapLogger executing search failed.")
            return []

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

            self.Log(f"{email_info}")

        return new_email_infos