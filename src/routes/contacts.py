from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from pydantic import EmailStr

from sqlalchemy.orm import Session
from src.repository import contacts
from src.database.models import Contact, User
from src.database.db import get_db
from src.schemas import ContactResponse, ContactSchema, ContactUpdate
from src.services.auth import auth_service

router = APIRouter(tags=['contacts'])

@router.get("/search")
async def search_contacts_route(db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user), search_query: str = Query(..., min_length=1)):
    contacts_ = contacts.search_contacts(db, user, search_query)
    return {"contacts": contacts_}


@router.get("/", response_model=List[ContactResponse])
def get_contacts(limit: int = Query(10, ge=10, le=100), offset: int = Query(0, ge=0),
                 first_name: str = Query(default=None, max_length=10),
                 last_name: str = Query(default=None, max_length=15),
                 email: EmailStr = Query(default=None, max_length=32),
                 db: Session = Depends(get_db),
                 user: User = Depends(auth_service.get_current_user)):
    contacts_ = contacts.get_contacts(limit, offset, db, user, first_name, last_name, email)
    if contacts_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts_


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                user: User = Depends(auth_service.get_current_user)):
    contact = contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(body: ContactSchema, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(body: ContactUpdate, contact_id: int = Path(ge=1), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = contacts.delete_contact(contact_id, db, user)
    return contact
