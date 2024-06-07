from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import ContactSchema, ContactUpdate


def get_contacts(limit: int, offset: int, db: Session, user: User, first_name: str = None, last_name: str = None, email: EmailStr = None):
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
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = db.execute(stmt)
    return contact.scalar_one_or_none()


def create_contact(body: ContactSchema, db: Session, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(contact_id: int, body: ContactUpdate, db: Session, user: User):
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
    stmt = select(Contact).filter_by(user=user)
    if search_query:
        stmt = stmt.filter(
            (Contact.first_name.ilike(f'%{search_query}%')) |
            (Contact.last_name.ilike(f'%{search_query}%')) |
            (Contact.email.ilike(f'%{search_query}%'))
        )
    
    result = db.execute(stmt)
    return result.scalars().all()
