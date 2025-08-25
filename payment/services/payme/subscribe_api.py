from payment.services.payme import *
from app.utils import DictToClass


async def receipts_create_api(payment_id, amount):
    """
    Response: `receipt ID`
    """
    method = "receipts.create"
    params = {
        "amount": int(amount * 100),
        "account": {
            "account_id": str(payment_id)
        }
    }
    checkout_request = await CheckoutEndpointRequest.create(
        method, params, RequestType.POST
    )
    response = await checkout_request.send()
    receipt_id = response['result']['receipt']['_id']
    return receipt_id


async def receipts_pay_api(receipt_id, token) -> dict:
    """
    If "result" is available in response, then request is successfully.
    Otherwise, "error" is in response. It means request is not successfully
    """
    method = "receipts.pay"
    params = {
        "id": receipt_id,
        "token": token
    }
    checkout_request = await CheckoutEndpointRequest.create(
        method, params, RequestType.POST
    )
    response = await checkout_request.send()
    return response
