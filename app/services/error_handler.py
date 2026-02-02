from core.exceptions import *
from app.utils.tg_bot import send_newsletter_api
from config import ADMIN_TELEGRAM_ID

def run_on_error(exception):
    if isinstance(exception, OrderError):
        send_newsletter_api(ADMIN_TELEGRAM_ID, str(exception))