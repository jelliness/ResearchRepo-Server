import os
from dotenv import load_dotenv
import redis 
from datetime import datetime,timedelta,timezone

load_dotenv()
class Config:
    SECRET_KEY = os.environ['SECRET_KEY']

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SESSION_TYPE="redis"
    SESSION_PERMANENT=False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")

    REDIS_HOST = 'localhost' 
    REDIS_PORT = 6379  
    REDIS_DB = 0 

    JWT_TOKEN_EXPIRES = timedelta(hours=4)

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    DEFAULT_SENDER =os.environ.get('MAIL_USERNAME')

    OTP_MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')


    NOTIF_MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD') 
    




    

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
# app configuration (database settings)

