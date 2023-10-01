import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(recipient, subject, body):
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "apartment.rental.blue@gmail.com"
    password = "yfzx osym xwsy lycn"

    msg = MIMEMultipart()   
    msg['From'] = sender_email
    msg['To'] = recipient

    msg['Subject'] = subject
    body = MIMEText(body) 
    msg.attach(body)

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)