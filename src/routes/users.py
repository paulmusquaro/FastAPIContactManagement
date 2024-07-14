from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import pickle
import cloudinary
import cloudinary.uploader
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repositories_users
from src.schemas import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from dotenv import load_dotenv
import os
from fastapi_limiter.depends import RateLimiter
from src.services.email import send_email, send_recovery_email



load_dotenv()

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()



@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET endpoint that returns the current user's information.

    :param current_user: User: Get the current user
    :return: The current user object
    """
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), 
                            current_user: User = Depends(auth_service.get_current_user),
                            db: Session = Depends(get_db)):
    """
    The update_avatar_user function is used to update the avatar of a user.
        The function takes in an UploadFile object, which contains the file that will be uploaded to Cloudinary.
        It also takes in a User object, which is obtained from auth_service's get_current_user function.
        Finally it takes in a Session object, which is obtained from get_db().

    :param file: UploadFile: Upload the file to cloudinary
    :param current_user: User: Get the current user's email
    :param db: Session: Connect to the database
    :return: The user object with the updated avatar
    """
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True)

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repositories_users.update_avatar(current_user.email, src_url, db)
    await auth_service.r.set(user.email, pickle.dumps(user))
    await auth_service.r.expire(user.email, 300)
    return user



@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: Session = Depends(get_db)):
    """
    The signup function creates a new user account. It checks if the email is already in use and raises an exception if it is.
    Otherwise, it hashes the password, creates a new user, and returns the new user object.

    :param body: UserSchema: The data for the new user
    :param db: Session: Provide the database session
    :return: The newly created User object
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    return new_user



@router.post("/login",  response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function authenticates a user and generates JWT tokens.
    It checks if the email and password are correct, and if they are, generates and returns access and refresh tokens.

    :param body: OAuth2PasswordRequestForm: The login credentials
    :param db: Session: Provide the database session
    :return: A dictionary with access_token, refresh_token, and token_type
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token',  response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: Session = Depends(get_db)):
    """
    The refresh_token function generates new access and refresh tokens using a valid refresh token.
    It checks the validity of the refresh token and updates it in the database.

    :param credentials: HTTPAuthorizationCredentials: The refresh token credentials
    :param db: Session: Provide the database session
    :return: A dictionary with new access_token, refresh_token, and token_type
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}', dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function confirms the user's email using a token sent to their email address.
    It checks the validity of the token and updates the user's confirmed status in the database.

    :param token: str: The token sent to the user's email
    :param db: Session: Provide the database session
    :return: A dictionary with a confirmation message
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email', dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function sends a confirmation email to the user.
    It checks if the email is already confirmed and, if not, sends a confirmation email.

    :param body: RequestEmail: The email request data
    :param background_tasks: BackgroundTasks: Background tasks for sending emails
    :param request: Request: The request object
    :param db: Session: Provide the database session
    :return: A dictionary with a confirmation message
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post('/recovery_password', dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def recovery_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The recovery_email function sends a recovery email to the user.
    If the user's email matches the request email, it sends instructions to reset the password.

    :param body: RequestEmail: The email request data
    :param background_tasks: BackgroundTasks: Background tasks for sending emails
    :param request: Request: The request object
    :param db: Session: Provide the database session
    :return: A dictionary with a recovery message
    """
    user = await repositories_users.get_user_by_email(body.email, db)
    if user and user.email == body.email:
        background_tasks.add_task(send_recovery_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for instruction to recovery."}


@router.get('/recovered_password/{token}', dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def recovered_password(new_password: str, token: str, db: Session = Depends(get_db)):
    """
    The recovered_password function resets the user's password using a token sent to their email.
    It hashes the new password and updates it in the database.

    :param new_password: str: The new password
    :param token: str: The token sent to the user's email
    :param db: Session: Provide the database session
    :return: A dictionary with a password reset message
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recovering error")
    user.password = auth_service.get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password was successfully reseted"}