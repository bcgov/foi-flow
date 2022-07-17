
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

    
    def send(self, content, attachment):
        msg = MIMEMultipart("alternative")
        msg['From'] = os.getenv('EMAIL_SRUSERID')
        msg['To'] = "sumathi.thirumani@aot-technologies.com"
        msg['Subject'] = "Hello email"
        part = MIMEText(content, "html")
        msg.attach(part)
        # Add Attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment)
   
        encoders.encode_base64(part)

    # Set mail headers
        part.add_header(
        "Content-Disposition",
        "attachment", filename= "fee.pdf"
        )
        msg.attach(part)
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtpobj:
                smtpobj.ehlo()
                smtpobj.starttls()
                smtpobj.ehlo()
                smtpobj.login(os.getenv('EMAIL_SRUSERID'), os.getenv('EMAIL_SRPWD'))
                smtpobj.sendmail(os.getenv('EMAIL_SRUSERID'),  msg['To'], msg.as_string())
                smtpobj.quit()
        except Exception as e:
            print(e)
        return None
    

        