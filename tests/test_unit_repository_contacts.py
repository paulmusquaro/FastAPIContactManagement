import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.repository.contacts import get_contacts, get_contact, create_contact, update_contact, delete_contact, search_contacts
from src.schemas import ContactSchema, ContactUpdate
from pydantic import EmailStr
import datetime


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.user = User(id=1, email="person2025.ua", username="test_user", password="1234566", confirmed=True)
        self.contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phonenumber='1234567899999', user=self.user)
        self.session = MagicMock(spec=Session)

    async def test_get_contacts(self):
        self.session.execute.return_value.scalars.return_value.all.return_value = [self.contact]
        result = get_contacts(10, 0, self.session, self.user)
        self.assertEqual(result, [self.contact])

    async def test_get_contact(self):
        self.session.execute.return_value.scalar_one_or_none.return_value = self.contact
        result = get_contact(self.contact.id, self.session, self.user)
        self.assertEqual(result, self.contact)

    async def test_create_contact(self):
        body = ContactSchema(first_name="Jane", last_name="Doeno", email="jane.doe@example.com", phonenumber='1234567890000', additional_info='qwwerttyuio')
        result = create_contact(body, self.session, self.user)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)

    async def test_update_contact(self):
        birthdate = datetime.datetime.strptime('2019-12-04', '%Y-%m-%d').date()
        body = ContactUpdate(first_name="Jane", last_name="Doeno", email="jane.doe@example.com", phonenumber='1234567890000', birthdate=birthdate, additional_info='qwwerttyuio')
        self.session.execute.return_value.scalar_one_or_none.return_value = self.contact
        result = update_contact(self.contact.id, body, self.session, self.user)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.assertEqual(result.first_name, body.first_name)

    async def test_delete_contact(self):
        self.session.execute.return_value.scalar_one_or_none.return_value = self.contact
        result = delete_contact(self.contact.id, self.session, self.user)
        self.session.commit.assert_called_once()
        self.assertEqual(result, self.contact)

    async def test_search_contacts(self):
        self.session.execute.return_value.scalars.return_value.all.return_value = [self.contact]
        result = search_contacts(self.session, self.user, "John")
        self.assertEqual(result, [self.contact])