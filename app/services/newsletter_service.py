from celery import shared_task
import requests
from config import WEBHOOK_URL


@shared_task
def send_newsletter_api(bot_user_id: int, text: str):
    # get current host
    API_URL = f"{WEBHOOK_URL}/send-newsletter/"
    data = {
        "user_id": bot_user_id,
        "text": text
    }
    requests.post(API_URL, json=data)
