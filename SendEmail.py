
import smtplib
from BaseObject import BaseObject
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate
import base64


class SendEmail(BaseObject):
    def __init__(self, recipients_lookup,email_list=""):
        super(SendEmail, self).__init__()
        if hasattr(self, "_config") and hasattr(self._config, "emailfrom"):
            self.me = self._config.emailfrom
            try:
                self.to = self._config.emaillookup[recipients_lookup]
            except KeyError:
                if email_list:
                    self.to = email_list
                else:
                    raise Exception("No email receipt supplied")
        self.log("SendEmail initialised")

    def send_email_with_files(self,files,subject="Report", body_text=""):
        self.log("Sending email ->\t{0}\t{1}".format(str(self.to), str(files)))
        self.log("SMTP settings:%s, %s" % (self._config.smtpserver, self._config.smtpport))
        try:
            msg = MIMEMultipart(boundary="-------------------------boundary")
            msg['From'] = self.me.encode('utf-8')
            msg['To'] = COMMASPACE.join(self.to)
            msg['Subject'] = subject.encode('utf-8')
            msg['Date'] = formatdate(localtime=True)
            msg.attach(MIMEText(body_text+"\nPlease do not reply to this email - this account is not monitored."))
            for f in files or []:
                with open(f, "rb") as fil:
                    part = MIMEApplication(fil.read(),Name=basename(f))
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                msg.attach(part)

            if not hasattr(self._config,"smtpserver") or not hasattr(self._config,"smtpport"):
                raise Exception("SMTP details not provided in configuration")
            smtp = smtplib.SMTP(self._config.smtpserver, self._config.smtpport)
            smtp.ehlo()
            smtp.starttls()
            smtp.sendmail(self.me, self.to, msg.as_string())
            smtp.close
        except Exception as e:
            self.errorlog(e.message)