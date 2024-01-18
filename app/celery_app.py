from celery import Celery
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv('.env')

app = Celery('app', broker='pyamqp://guest@rabbitmq//')

@app.task
def send_confirmation_email(user_email):
    msg = MIMEMultipart()
    msg['From'] = os.environ['YOUR_EMAIL']
    msg['To'] = user_email
    msg['Subject'] = 'Register confirmation'
    body = 'Thank you for registering!'
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(os.environ['YOUR_EMAIL'], os.environ['YOUR_PASSWORD'])
    server.send_message(msg)
    server.quit()


