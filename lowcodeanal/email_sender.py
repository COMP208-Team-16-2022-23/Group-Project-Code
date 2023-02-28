from flask_mail import Message
from lowcodeanal.app import mail


def send(recipients, subject, body):
    msg = Message(subject, recipients=recipients)
    msg.body = body
    try:
        mail.send(msg)  # Flask-Mail instance named mail
    except Exception as e:
        return str(e)
    return 0
