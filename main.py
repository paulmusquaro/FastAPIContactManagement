
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text, and_, select, extract
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.routes import contacts, dates


app = FastAPI()
app.include_router(contacts.router, prefix="/contacts")
app.include_router(dates.router, prefix="/dates")


@app.get("/")
def test(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to Contacts API!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
