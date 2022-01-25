import imaplib
import email
from email.header import decode_header
import os
import socket
from dotenv import load_dotenv, find_dotenv
from time import sleep

load_dotenv(find_dotenv())
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_PORT = os.getenv('IMAP_PORT')
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT')
PERIOD_CHECK = int(os.getenv('PERIOD_CHECK'))


HOST = '127.0.0.1'
PORT = 20000
s = socket.socket()
s.connect((HOST, PORT))
answer_id = s.recv(1024).decode()
print(answer_id)


# учетные данные
def clean(text):
    # чистый текст для создания папки
    return "".join(c if c.isalnum() else "_" for c in text)


# create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL(IMAP_HOST)
# authenticate
imap.login(EMAIL_LOGIN, EMAIL_PASSWORD)
# количество популярных писем для получения
k = 0
while k != 2:
    status, messages = imap.select("INBOX")
    N = int(messages[0])
    # общее количество писем
    messages = int(messages[0])
    for i in range(messages, messages - N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                if subject == answer_id:
                    print(From)
                    print(subject)
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            print(body)
                    print("=" * 100)
                    log = open('success_request.log', 'a')
                    log.write("%s: %s\n" % (subject, body))
                    log.close()
                else:
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                    log1 = open('error_request.log', 'a')
                    log1.write("%s: %s\n" % (subject, body))
                    log1.close()
    k += 1
    sleep(PERIOD_CHECK)
imap.close()
imap.logout()
