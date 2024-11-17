from flask_mailman import EmailMessage
from flask import current_app
from app.config import Config

def send_otp_email(to_email, subject, body):
    # Use the OTP email password
    #current_app.config['MAIL_PASSWORD'] = Config.OTP_MAIL_PASSWORD

    #print(Config.OTP_MAIL_PASSWORD)
    
    # Create and send the email
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=Config.DEFAULT_SENDER,
        to=[to_email]
    )
    with current_app.app_context():
        email.send()

def send_notification_email(to_email, subject, body):
    # Create and send the email

    current_app.config['MAIL_PASSWORD'] = Config.NOTIF_MAIL_PASSWORD
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=Config.DEFAULT_SENDER,
        to=[to_email]
    )
    with current_app.app_context():
        email.send()
