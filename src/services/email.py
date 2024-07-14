from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.services.auth import auth_service
from dotenv import load_dotenv
import os

load_dotenv()



conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=os.getenv("MAIL_PORT"),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME="Desired Name",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three parameters:
            -email: EmailStr, the user's email address.
            -username: str, the username of the user who is registering for an account.  This will be used in a greeting message within the body of the email sent to them.
            -host: str, this is used as part of a URL that will be included in an HTML template for sending emails.

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the template
    :param host: str: Pass in the hostname of the server to be used in the email template
    :return: A coroutine object
    """
    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_recovery_email(email: EmailStr, username: str, host: str):
    """
    The send_recovery_email function sends an email to the user with a link to reset their password.
        Args:
            email (str): The user's email address.
            username (str): The user's username.
            host (str): The hostname of the server where this function is being called from.

    :param email: EmailStr: Specify the email address of the user
    :param username: str: Personalize the email message
    :param host: str: Pass the host url to the template
    :return: A coroutine object, which is a special type of object that can be used with asyncio
    """
    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_recovery_template.html")
    except ConnectionErrors as err:
        print(err)