# FastAPIContactManagement


This project is a REST API for managing contact information, built using FastAPI and SQLAlchemy with PostgreSQL as the database backend. It allows for creating, retrieving, updating, deleting contact details and fetching contacts with upcoming birthdays.

## Features

- CRUD operations: Create, Read, Update, Delete contacts.
- Search contacts by firstname, lastname, or email.
- Get contacts with birthdays in the next 7 days.
- Creating an account and logging in.
- Update Avatar.
- Password Reset.
- Email Confirmation.
- Pydantic models for data validation.
- Auto-generated API documentation using Swagger UI.

## Technologies

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+.
- **SQLAlchemy**: The Python SQL Toolkit and Object-Relational Mapper.
- **PostgreSQL**: An open-source relational database.
- **Redis**: Key-value database for cache.
- **Pydantic**: Data validation and settings management using Python type annotations.

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis


### Running the Application

1. Run database in Docker container.

   ```
   docker-compose -f docker-compose.yaml up --force-recreate
   ```

2. Start the FastAPI server:
   ```sh
   uvicorn main:app --host localhost --port 8000 --reload
   ```
3. Access the Swagger UI documentation at `http://127.0.0.1:8000/docs`.

## Usage

The API supports the following operations:

- **Create a Contact**: `POST /contacts/`
- **List all Contacts**: `GET /contacts/`
- **Retrieve a Contact by ID**: `GET /contacts/{contact_id}`
- **Update a Contact**: `PUT /contacts/{contact_id}`
- **Delete a Contact**: `DELETE /contacts/{contact_id}`
- **Contacts with Upcoming Birthdays**: `GET /dates/`
- **Search Contacts**: `GET /contacts/search?search_query=...`


Refer to the Swagger UI documentation for more details on request and response formats.