
from os import stat
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class senderservice:
    """ FOI Assignee management service

    This service wraps up send operations.

    """

    
    def send(self, content, _messageattachmentlist, requestjson):
        msg = MIMEMultipart("alternative")
        msg['From'] = os.getenv('EMAIL_SRUSERID')
        msg['To'] = requestjson["email"]
        msg['Subject'] = "Your FOI Request ["+requestjson["axisRequestId"]+"]"
        part = MIMEText(content, "html")
        msg.attach(part)
        # Add Attachment and Set mail headers
        for attachment in _messageattachmentlist:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.get('file').content)
            encoders.encode_base64(part)
            part.add_header(
            "Content-Disposition",
            "attachment", filename= attachment.get('filename')
            )
            msg.attach(part)
        try:
            with smtplib.SMTP(os.getenv('EMAIL_SERVER_SMTP'), os.getenv('EMAIL_SERVER_SMTP_PORT')) as smtpobj:
                smtpobj.ehlo()
                smtpobj.starttls()
                smtpobj.ehlo()
                smtpobj.login(os.getenv('EMAIL_SRUSERID'), os.getenv('EMAIL_SRPWD'))
                smtpobj.sendmail(os.getenv('EMAIL_SRUSERID'),  msg['To'], msg.as_string())
                smtpobj.quit()
        except Exception as e:
            print(e)
        return None
    

        