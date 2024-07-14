from fastapi import Depends
from sqlalchemy import select
from libgravatar import Gravatar
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserSchema


async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists, it returns None.

    :param email: str: Specify the type of data that is expected to be passed in
    :param db: Session: Pass the database session into the function
    :return: The first user with the given email from the database
    """
    stmt = select(User).filter_by(email=email)
    user = db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: Session = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
        Args:
            body (UserModel): The UserModel object to be created.
            db (Session): The SQLAlchemy session object used for querying the database.

    :param body: UserModel: Create a new user object
    :param db: Session: Access the database
    :return: A user object
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    # new_user = User(**body.model_dump(), avatar=avatar)
    # db.add(new_user)
    # db.commit()
    # db.refresh(new_user)
    # return new_user

    new_user_data = body.dict()
    new_user_data['avatar'] = avatar
    new_user = User(**new_user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session):
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user in the database
    :param token: str | None: Update the user's refresh token
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Pass in the email address of the user who is trying to log in
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that is expected to be passed into the function
    :param db: Session: Pass the database session to the function
    :return: The user object after updating the avatar
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user