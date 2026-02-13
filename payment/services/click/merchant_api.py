from config import CLICK_SERVICE_ID
from payment.services.click import *


def payment_cancel(click_paydoc_id: int) -> dict:
    """
    Reverses a payment.

    Args:
        click_paydoc_id (int): Payment document ID.

    Returns:
        dict: {
            "error_code": int,
            "error_note": str,
            "payment_id": int
        }

    Example response:
        {
            "error_code": 0,
            "error_note": "Success",
            "payment_id": 1234567
        }
    """
    url = ClickEndpointRequest.get_reversal_url(click_paydoc_id)
    request = ClickEndpointRequest(
        url=url,
        type=RequestType.DELETE
    )
    response = request.send()
    return response


