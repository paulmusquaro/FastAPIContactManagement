
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text, and_, select, extract
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.routes import contacts, dates, users
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI()
app.include_router(users.router, prefix="/users")
app.include_router(contacts.router, prefix="/contacts")
app.include_router(dates.router, prefix="/dates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)



@app.get("/")
async def test(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to Contacts API!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
