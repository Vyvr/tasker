import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Tasker")
DATABASE_URL = os.getenv("DATABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set.")

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not set.")

if not CSRF_SECRET_KEY:
    raise ValueError("CSRF_SECRET_KEY is not set.")
