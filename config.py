
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-later")
    DEBUG = True
    DATABASE = os.path.join(BASE_DIR, "instance", "mountain_mart.db")
