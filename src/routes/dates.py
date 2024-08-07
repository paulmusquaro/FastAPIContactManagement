from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select, extract, and_, or_
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas import ContactResponse
from src.services.auth import auth_service

router = APIRouter(tags=['dates'])


@router.get("/", response_model=List[ContactResponse])
def show_dates(db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The show_dates function retrieves contacts whose birthdays fall within the next 7 days.

    :param db: Session: Provide the database session
    :param user: User: Get the current user from the authentication service
    :return: A list of contacts whose birthdays are within the next 7 days
    """
    today = date.today()
    end_date = today + timedelta(days=7)

    stmt = select(Contact).filter_by(user=user).filter(
        and_(
            or_(
                and_(
                    extract('month', Contact.birthdate) == today.month,
                    extract('day', Contact.birthdate) >= today.day
                ),
                and_(
                    extract('month', Contact.birthdate) == end_date.month,
                    extract('day', Contact.birthdate) <= end_date.day
                )
            )
        )
    )
    contacts = db.execute(stmt)
    return contacts.scalars().all()
