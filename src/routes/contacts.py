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
    """
    The search_contacts_route function searches for contacts based on a query string.

    :param db: Session: Provide the database session
    :param user: User: Get the current user from the authentication service
    :param search_query: str: The search query string
    :return: A dictionary with the list of contacts that match the search query
    """
    contacts_ = contacts.search_contacts(db, user, search_query)
    return {"contacts": contacts_}


@router.get("/", response_model=List[ContactResponse])
def get_contacts(limit: int = Query(10, ge=10, le=100), offset: int = Query(0, ge=0),
                 first_name: str = Query(default=None, max_length=10),
                 last_name: str = Query(default=None, max_length=15),
                 email: EmailStr = Query(default=None, max_length=32),
                 db: Session = Depends(get_db),
                 user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function retrieves a list of contacts based on the provided query parameters.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: The number of contacts to skip before starting to collect the result set
    :param first_name: str: Filter contacts by first name
    :param last_name: str: Filter contacts by last name
    :param email: EmailStr: Filter contacts by email
    :param db: Session: Provide the database session
    :param user: User: Get the current user from the authentication service
    :return: A list of contacts that match the provided filters
    """
    contacts_ = contacts.get_contacts(limit, offset, db, user, first_name, last_name, email)
    if contacts_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts_


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function retrieves a contact by its ID.

    :param contact_id: int: The ID of the contact to retrieve
    :param db: Session: Provide the database session
    :param user: User: Get the current user from the authentication service
    :return: The contact that matches the provided ID
    """
    contact = contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(body: ContactSchema, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact.

    :param body: ContactSchema: The schema of the contact to create
    :param db: Session: Provide the database session
    :param user: User: Get the current user from the authentication service
    :return: The created contact
    """
    contact = contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(body: ContactUpdate, contact_id: int = Path(ge=1), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates an existing contact.

    :param body: ContactUpdate: The updated data for the contact
    :param contact_id: int: The ID of the contact to update
    :param db: Session: Provide the database session
    :param user: User: Get the current user from the authentication service
    :return: The updated contact
    """
    contact = contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact by its ID.

    :param contact_id: int: The ID of the contact to delete
    :param db: Session: Provide the database session
    :param user: User: Get the current user from the authentication service
    :return: The deleted contact
    """
    contact = contacts.delete_contact(contact_id, db, user)
    return contact
