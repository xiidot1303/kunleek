from config import *
from app.utils import send_request, create_random_id
from asgiref.sync import async_to_sync

checkout_url = PAYME_CHECKOUT_URL


class RequestType:
    POST = 'post'
    GET = 'get'


class CheckoutEndpointRequest:
    def __init__(self, method, params, type, request_body):
        self.request_method = method
        self.request_params = params
        self.request_type = type
        self.request_body = request_body
        self.headers = {
            'X-Auth': f'{PAYME_CASH_ID}:{PAYME_KEY}',
            'Content-Type': 'application/json',
        }

    @classmethod
    async def create(cls, method, params, type):
        request_body = {
            "jsonrpc": "2.0",
            "id": await create_random_id(),
            "method": method,
            "params": params
        }
        instance = cls(method, params, type, request_body)
        return instance

    async def send(self):
        # change x-auth if request is cards. | x-auth should only cash id
        if "cards." in self.request_method:
            self.headers['X-Auth'] = PAYME_CASH_ID
        response = await send_request(
            checkout_url, self.request_body, self.headers, self.request_type
        )
        return response
