from config import CLICK_SERVICE_ID
from payment.services import *
from payment.services.click import *
from payment.models import Click_transaction


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


def payment_submit_ofd(account: Account) -> dict:
    """
    Submits a payment for off-line processing.

    Args:
        Account (obj): Account obj.

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
    url = f"{CLICK_API_ENDPOINT}/payment/ofd_data/submit_items"
    click_trans: Click_transaction = Click_transaction.objects.get(
        order_id=account.id)
    items = get_items_by_account_id(account.id)
    fiscal_items = [
        {
            "Name": item.get("product__name"),
            "SPIC": item.get("product__mxik"),
            "PackageCode": item.get("product__package_code"),
            "Price": int(int(item.get("price")) / 1.12 * item.get("quantity") * 100),
            "Amount": item.get("quantity"),
            "VAT": int(0.12 * int(item.get("price"))/1.12 * 100),
            "VATPercent": 12,
            "CommissionInfo": {
                "TIN": "312027124"
            }

        }
        for item in items
    ]
    if account.delivery_price:
        fiscal_items.append(
            {
                "Name": "Delivery",
                "SPIC": "10107002001000000",
                "PackageCode": "1209885",
                "Price": int(float(account.delivery_price) / 1.12 * 100),
                "Amount": 1,
                "VAT": int(0.12 * float(account.delivery_price)/1.12 * 100),
                "VATPercent": 12,
                "CommissionInfo": {
                    "TIN": "312027124"
                }

            }
        )
    data = {
        "service_id": CLICK_SERVICE_ID,
        "payment_id": click_trans.click_paydoc_id,
        "items": fiscal_items,
        "received_card": click_trans.amount
    }

    request = ClickEndpointRequest(
        url=url,
        type=RequestType.POST,
        params=data
    )
    response = request.send()
    return response
