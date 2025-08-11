import os
from dotenv import load_dotenv

load_dotenv(os.path.join(".env"))

PORT = int(os.environ.get("PORT"))
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(",")

# Postgres db informations
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Telegram bot
BOT_API_TOKEN = os.environ.get("BOT_API_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
GROUP_ID = os.environ.get("GROUP_ID")

# Billz API
BILLZ_SECRET_TOKEN = os.environ.get("BILLZ_SECRET_TOKEN")

# Payme
PAYME_CASH_ID = os.environ.get("PAYME_CASH_ID")
PAYME_KEY = os.environ.get("PAYME_KEY")
PAYME_TEST_KEY = os.environ.get("PAYME_TEST_KEY")
PAYME_CHECKOUT_URL = os.environ.get("PAYME_CHECKOUT_URL")

# Click
CLICK_SERVICE_ID = os.environ.get("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = os.environ.get("CLICK_MERCHANT_ID")
CLICK_SECRET_KEY = os.environ.get("CLICK_SECRET_KEY")
CLICK_MERCHANT_USER_ID = os.environ.get("CLICK_MERCHANT_USER_ID")

GROUP_ID = os.environ.get("GROUP_ID")