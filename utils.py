from flask_mail import Message
from extensions import mail
from flask import current_app

def send_email(to, subject, body):
    msg = Message(
        subject=subject,
        recipients=[to],
        body=body,  # <- comma was missing here
        sender=current_app.config["MAIL_DEFAULT_SENDER"]
    )
    mail.send(msg)
