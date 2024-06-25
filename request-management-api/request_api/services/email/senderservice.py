
from audioop import reverse
from os import stat
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

from email import encoders
from request_api.services.email.templates.templateconfig import templateconfig
import imaplib
from imap_tools import MailBox, AND
import logging
import email
import json
from request_api.services.external.storageservice import storageservice
from request_api.models.default_method_result import DefaultMethodResult


MAIL_SERVER_SMTP = os.getenv('EMAIL_SERVER_SMTP')
MAIL_SERVER_SMTP_PORT = os.getenv('EMAIL_SERVER_SMTP_PORT')
MAIL_SERVER_IMAP = os.getenv('EMAIL_SERVER_IMAP')
MAIL_SRV_USERID = os.getenv('EMAIL_SRUSERID')
MAIL_SRV_PASSWORD = os.getenv('EMAIL_SRPWD')
MAIL_FROM_ADDRESS = os.getenv('EMAIL_SENDER_ADDRESS')
MAIL_FOLDER_OUTBOX = os.getenv('EMAIL_FOLDER_OUTBOX')
MAIL_FOLDER_INBOX = os.getenv('EMAIL_FOLDER_INBOX')
class senderservice:
    """ Email Sender service

    This service wraps up send operations.

    """

    def send_by_request(self, subject, content, _messageattachmentlist, requestjson):
        return self.send(subject, content, _messageattachmentlist, requestjson["email"])

    def send(self, subject, content, _messageattachmentlist, emails):
        logging.debug("Begin: Send email for request ")
        content = content.replace('src=\\\"', 'src="')
        content = content.replace('\\\">','">')
        msg = MIMEMultipart('alternative')
        msg['From'] = MAIL_FROM_ADDRESS
        msg['To'] = ",".join(emails)
        msg['Subject'] = subject
        part = MIMEText("""<html>
<body>
<img src="data:image/jpeg;base64,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" alt="Logo" style="max-width: 100; height: 100;">
</body>
</html>""", "html")
        msg.attach(part)
        # Add Attachment and Set mail headers
        """
        for attachment in _messageattachmentlist:
            file = storageservice().download(attachment['url'])
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.content)
            encoders.encode_base64(part)
            part.add_header(
            "Content-Disposition",
            "attachment", filename= attachment.get('filename')
            )
            msg.attach(part)
        
        img = 'data:image/jpeg;base64,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'
        msgImg = MIMEImage(img, 'jpeg')
        msgImg.add_header('Content-ID', '<image1>')
        msgImg.add_header('Content-Disposition', 'inline', filename='signaure.jpeg')
        msg.attach(msgImg)
        """
        try:
            with smtplib.SMTP(MAIL_SERVER_SMTP,  MAIL_SERVER_SMTP_PORT) as smtpobj:
                smtpobj.ehlo()
                smtpobj.starttls()
                smtpobj.ehlo()
                #smtpobj.login(MAIL_SRV_USERID, MAIL_SRV_PASSWORD)
                smtpobj.sendmail(msg['From'],  msg['To'], msg.as_string())
                smtpobj.quit()
                logging.debug("End: Send email for request")
                return DefaultMethodResult(True,'Sent successfully', -1)    
        except Exception as e:
            logging.exception(e)
        return DefaultMethodResult(False,'Unable to send', -1)    
    

    def read_outbox_as_bytes(self, servicekey, requestjson):
        logging.debug("Begin: Read sent item for request = "+json.dumps(requestjson))
        _subject = templateconfig().getsubject(servicekey, requestjson)
        try:
            mailbox = MailBox(MAIL_SERVER_IMAP)
            mailbox.login(MAIL_SRV_USERID, MAIL_SRV_PASSWORD)
            #Navigate to sent Items
            is_exists = mailbox.folder.exists(MAIL_FOLDER_OUTBOX)
            if is_exists == True:
                mailbox.folder.set(MAIL_FOLDER_OUTBOX)
            messages = mailbox.fetch(criteria=AND(subject=_subject), reverse = True) 
            for message in messages:
                logging.debug("End: Read sent item for request = "+json.dumps(requestjson))
                return message.obj.__bytes__()
        except Exception as ex:
            logging.exception(ex)
        logging.debug("End: Read sent item for request = "+json.dumps(requestjson))
        return None     
        
           
