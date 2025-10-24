# Stores all configuration values
import certifi
import os


SECRET_KEY = os.environ.get('SECRET_KEY')
MONGODB_HOST = os.environ.get('MONGODB_HOST')

GOOGLE_FORM_LINK = os.environ.get('GOOGLE_FORM_LINK')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')


