import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from sqlalchemy.orm import Session
from src.database.models import User, Contact
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar
from src.schemas import UserSchema


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        # Створюємо мок об'єкт User
        self.user = User(
            id=1,
            username="string",
            email="com@com.com",
            password="string",
            # avatar=None,
            # refresh_token=None,
            # confirmed=True,
            # created_at=None,
            # updated_at=None
        )
        # Створюємо мок об'єкт Session
        self.session = MagicMock()
        # Налаштовуємо мок для методу query().filter().first()
        self.session.query().filter().first.return_value = self.user

    async def test_user_by_email(self):
        email="com@com.com"
        result = await get_user_by_email(email, self.session)
        self.assertEqual(result, self.user)
        self.assertEqual(result.email, self.user.email)

    async def test_create_user(self):
        body = User(username="stringg", email="gcom@com.com", password="string")
        result = await create_user(body, self.session)
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, User)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.username,body.username)

    async def test_update_token(self):
        token = "secret_hash"
        result = await update_token(self.user, token, self.session)
        self.session.commit.assert_called_once()
        self.assertEqual(self.user.refresh_token, token)

    async def test_confirmed_email(self):
        email = "com@com.com"
        with patch('src.repository.users.get_user_by_email') as mock:
            mock.return_value = self.user
            await confirmed_email(email, self.session)
            self.session.commit.assert_called_once()
            self.assertTrue(self.user.confirmed)
            self.assertEqual(self.user.email, email)

    async def test_update_avatar(self):
        url = "https://www.google.com/search?q=postgres+logo&client=firefox-b-d&sca_esv=8476a88ce4ea74c6&sca_upv=1&udm=2&biw=1536&bih=739&sxsrf=ADLYWIISfB-o2BMF1CRtNsVjv9LcuSAE5A%3A1720920305439&ei=8SiTZvq-Gpr-7_UPw-6ZOA&ved=0ahUKEwi6-_fbr6WHAxUa_7sIHUN3BgcQ4dUDCBA&uact=5&oq=postgres+logo&gs_lp=Egxnd3Mtd2l6LXNlcnAiDXBvc3RncmVzIGxvZ28yBRAAGIAEMgYQABgHGB4yBhAAGAcYHjIGEAAYBxgeMgYQABgHGB4yBhAAGAcYHjIGEAAYBxgeMgYQABgHGB4yBhAAGAcYHjIGEAAYBxgeSMEcUMMGWJQacAF4AJABAJgB-AGgAZgMqgEFMC40LjS4AQPIAQD4AQGYAgigAqELwgIKEAAYgAQYQxiKBcICBxAAGIAEGBPCAggQABgTGAcYHpgDAIgGAZIHBTEuMy40oAeAKg&sclient=gws-wiz-serp#vhid=xO8Ayj3TZvqeDM&vssid=mosaic"
        with patch('src.repository.users.get_user_by_email') as mock:
            mock.return_value = self.user
            await update_avatar(self.user.email, url, self.session)
            self.session.commit.assert_called_once()
            self.assertEqual(self.user.avatar, url)