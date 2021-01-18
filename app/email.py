from flask_mail import Message
from app import mail

def send_email(subject, sender, recipients, html_body):
    msg = Message(subject = subject, recipients = recipients, sender = sender)
    msg.html = html_body
    mail.send(msg)