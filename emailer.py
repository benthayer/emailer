import sys
import os
from glob import glob

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate


def send(subject, content, to=None, html=False, images=[]):
    addr = os.getenv('EMAIL_SENDER')

    msg = MIMEMultipart()

    msg['From'] = addr
    if to is None:
        to = addr
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)

    msg['Subject'] = subject

    if html:
        msg.attach(MIMEText(content, 'html'))
    else:
        msg.attach(MIMEText(content))

    for image_path in images:
        with open(image_path, 'rb') as image:
            mime_image = MIMEImage(image.read(), _subtype=image_path.split('.')[-1])
        mime_image.add_header('Content-ID', '<' + image_path + '>')
        msg.attach(mime_image)

    s = smtplib.SMTP(os.getenv('SMTP_HOST'), os.getenv('SMTP_PORT', 465))
    s.ehlo()
    s.starttls()
    s.login(addr, os.getenv('EMAIL_PASSWORD'))
    s.sendmail(addr, [to], msg.as_string())
    print('Sent email')
    s.close()


def send_html():
    # Usage send-html <to>
    # Must be in path with `email.html` and `subject.txt`
    assert len(sys.argv) == 2
    images = []
    for extension in ['jpg', 'jpeg', 'svg', 'png']:
        images.extend(glob('*.' + extension))

    with open('subject.txt') as subject_file:
        subject = subject_file.read()

    with open('email.html') as content_file:
        content = content_file.read()

    send(subject, content, to=sys.argv[1], html=True, images=images)
