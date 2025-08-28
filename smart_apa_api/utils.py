# utils.py
from django.core.signing import TimestampSigner
from django.core.mail import send_mail
from django.urls import reverse
from exchangelib import Credentials, Account, Message, DELEGATE, Configuration

signer = TimestampSigner()

def generate_verification_token(email):
    return signer.sign(email)

def verify_token(token, max_age=86400):  # 24 hours default
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except Exception:
        return None

def send_verification_email(user):
    token = generate_verification_token(user.login)
    # verification_link = f"https://api-smart.apa.kz/verify-email/?token={token}"
    verification_link = f"https://devapi-smart.apa.kz/verify-email/?token={token}"
    # verification_link = f"http://localhost:8000/verify-email/?token={token}"

    # EWS Credentials
    credentials = Credentials(
        username='a.kerimbayev@apa.kz',  # Exchange domain and user
        password='9xWF9TZ+'      # password
    )
    config = Configuration(
        server='mail.apa.kz/EWS/Exchange.asmx',  # on-premises server
        credentials=credentials
    )

    # Connect to account
    account = Account(
        primary_smtp_address='a.kerimbayev@apa.kz',  # the sender email
        config=config,
        autodiscover=False,
        access_type=DELEGATE
    )

    # Create and send email
    message = Message(
        account=account,
        folder=account.sent,
        subject='Двухфакторная аутентификация',
        body=f'Для входа на сайт smart.apa.kz пройдите по ссылке: {verification_link}',
        to_recipients=[user.login]
    )
    message.send()