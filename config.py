import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Admin@123@localhost:5432/minipro"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"



RAZORPAY_KEY_ID = "your_key_id"
RAZORPAY_KEY_SECRET = "your_key_secret"
