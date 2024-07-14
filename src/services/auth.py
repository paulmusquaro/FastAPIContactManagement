from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import users as repository_users
import redis.asyncio as redis
import pickle
from dotenv import load_dotenv
import os

load_dotenv()



class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Represent the instance of the class
        :param plain_password: Compare the password entered by the user to see if it matches
        :param hashed_password: Compare the hashed password stored in the database to the plain text password entered by a user
        :return: True if the password is correct and false otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Represent the instance of the class
        :param password: str: Specify the password that we want to hash
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    r = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/auth/login")

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token.
            Args:
                - data (dict): A dictionary containing the claims to be encoded in the JWT.
                - expires_delta (Optional[float]): An optional parameter specifying how long, in seconds, the access token should last before expiring. If not specified, it defaults to 15 minutes.

        :param self: Represent the instance of a class
        :param data: dict: Pass the data to be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: An encoded access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The time in seconds until the token expires. Defaults to None, which sets it to 7 days from now.

        :param self: Make the function a method of the class
        :param data: dict: Pass in the data that we want to encode into the token
        :param expires_delta: Optional[float]: Set the expiration time for the refresh token
        :return: A refresh token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
        It will raise an exception if the token is invalid or has expired.
        If it's valid, it returns the email address of the user.

        :param self: Represent the instance of a class
        :param refresh_token: str: Decode the refresh token
        :return: The email of the user
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            if it's valid, otherwise raises an HTTPException with status code 401.

        :param self: Access the class attributes
        :param token: str: Pass the token from the request header
        :param db: Session: Pass the database session to the function
        :return: A user object
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)
        user = await self.r.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            await self.r.set(user_hash, pickle.dumps(user))
            await self.r.expire(user_hash, 100)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user

    async def create_email_token(self, data: dict):
        """
        The create_email_token function takes in a dictionary of data and returns a token.
        The token is created using the JWT library, which encodes the data into a string that can be decoded later.
        The function also adds an expiration date to the encoded data.

        :param self: Make the function a method of the class
        :param data: dict: Pass in the data that will be encoded
        :return: A token that is signed with the secret_key
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        The function uses PyJWT to decode the token, which is then used to retrieve the email address from its payload.

        :param self: Represent the instance of the class
        :param token: str: Pass the token that is sent to the user's email
        :return: The email that was encoded in the jwt token
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()