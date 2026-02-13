from config import (
    CLICK_SERVICE_ID,
    CLICK_MERCHANT_ID,
    CLICK_SECRET_KEY,
    CLICK_MERCHANT_USER_ID,
    CLICK_API_ENDPOINT
)
import time
import hashlib
import requests

def get_click_invoice_url(paymend_id, amount):
    url = 'https://my.click.uz/services/pay?service_id={service_id}&merchant_id={merchant_id}&amount={amount}&transaction_param={transaction_param}'
    url = url.format(
        service_id = CLICK_SERVICE_ID,
        merchant_id = CLICK_MERCHANT_ID,
        amount = amount,
        transaction_param = paymend_id
    )
    return url


class RequestType:
    POST = 'post'
    GET = 'get'
    DELETE = 'delete'


class ClickEndpointRequest:
    def __init__(self, url, type: str, params: dict = None):
        self.params = params
        self.url = url
        self.type = type
        self.request_body = params
        timestamp = str(int(time.time()))
        raw_string = timestamp + CLICK_SECRET_KEY
        digest = hashlib.sha1(raw_string.encode('utf-8')).hexdigest()
        
        # Build Auth header
        auth_header = f"{CLICK_MERCHANT_USER_ID}:{digest}:{timestamp}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Auth": auth_header
        }
        self.headers = headers

    def send(self):
        if self.type == RequestType.POST:
            response = requests.post(self.url, json=self.request_body, headers=self.headers)
        elif self.type == RequestType.GET:
            response = requests.get(self.url, params=self.params, headers=self.headers)
        elif self.type == RequestType.DELETE:
            response = requests.delete(self.url, json=self.request_body, headers=self.headers)
        else:
            raise ValueError("Invalid request type")

        return response.json()
    
    @staticmethod
    def get_reversal_url(payment_id):
        """
        Args: 
            payment_id: bigint (click_paydoc_id)
        """
        url = f"{CLICK_API_ENDPOINT}/payment/reversal/{CLICK_SERVICE_ID}/{payment_id}"
        return url