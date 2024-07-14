from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import ContactSchema, ContactUpdate


def get_contacts(limit: int, offset: int, db: Session, user: User, first_name: str = None, last_name: str = None, email: EmailStr = None):
    """
    The get_contacts function retrieves a list of contacts for a specific user, with optional filtering
    by first name, last name, and email. The result is limited and offset based on the provided parameters.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Offset the starting point of the returned contacts
    :param db: Session: Provide the database session
    :param user: User: Identify the user whose contacts are to be retrieved
    :param first_name: str: Optional filter for the contact's first name
    :param last_name: str: Optional filter for the contact's last name
    :param email: EmailStr: Optional filter for the contact's email
    :return: A list of Contact objects
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    if first_name:
        stmt = stmt.filter(Contact.first_name.like(f'%{first_name}%'))
    if last_name:
        stmt = stmt.filter(Contact.last_name.like(f'%{last_name}%'))
    if email:
        stmt = stmt.filter(Contact.email.like(f'%{email}%'))
    contacts = db.execute(stmt)
    return contacts.scalars().all()


def get_contact(contact_id: int, db: Session, user: User):
    """
    The get_contact function retrieves a specific contact by its ID for a given user.

    :param contact_id: int: The ID of the contact to be retrieved
    :param db: Session: Provide the database session
    :param user: User: Identify the user whose contact is to be retrieved
    :return: The Contact object if found, otherwise None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = db.execute(stmt)
    return contact.scalar_one_or_none()


def create_contact(body: ContactSchema, db: Session, user: User):
    """
    The create_contact function creates a new contact for a given user in the database.

    :param body: ContactSchema: The data for the new contact
    :param db: Session: Provide the database session
    :param user: User: Identify the user to whom the new contact will belong
    :return: The newly created Contact object
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(contact_id: int, body: ContactUpdate, db: Session, user: User):
    """
    The update_contact function updates the details of an existing contact for a given user.

    :param contact_id: int: The ID of the contact to be updated
    :param body: ContactUpdate: The updated data for the contact
    :param db: Session: Provide the database session
    :param user: User: Identify the user whose contact is to be updated
    :return: The updated Contact object if found, otherwise None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = db.execute(stmt)
    contact: Contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phonenumber = body.phonenumber
        contact.birthdate = body.birthdate
        contact.additional_info = body.additional_info
        db.commit()
        db.refresh(contact)
    return contact



def delete_contact(contact_id: int, db: Session, user: User):
    """
    The delete_contact function deletes an existing contact for a given user.

    :param contact_id: int: The ID of the contact to be deleted
    :param db: Session: Provide the database session
    :param user: User: Identify the user whose contact is to be deleted
    :return: The deleted Contact object if found, otherwise None
    """
    stmt = select(Contact).filter_by(id=contact_id, user = user)
    contact = db.execute(stmt).scalar_one_or_none()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

# def search_contacts(db: Session, search_query: str):

#     stmt = select(Contact).where(
#         (Contact.first_name.ilike(f'%{search_query}%')) |
#         (Contact.last_name.ilike(f'%{search_query}%')) |
#         (Contact.email.ilike(f'%{search_query}%'))
#     )

#     result = db.execute(stmt)
#     return result.scalars().all()

def search_contacts(db: Session, user: User, search_query: str):
    """
    The search_contacts function searches for contacts of a given user based on a search query.

    :param db: Session: Provide the database session
    :param user: User: Identify the user whose contacts are to be searched
    :param search_query: str: The search query to filter contacts
    :return: A list of Contact objects matching the search query
    """
    stmt = select(Contact).filter_by(user=user)
    if search_query:
        stmt = stmt.filter(
            (Contact.first_name.ilike(f'%{search_query}%')) |
            (Contact.last_name.ilike(f'%{search_query}%')) |
            (Contact.email.ilike(f'%{search_query}%'))
        )
    
    result = db.execute(stmt)
    return result.scalars().all()
