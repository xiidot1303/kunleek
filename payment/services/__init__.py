from app.services.order_service import (
    get_order_by_id as get_account_by_id,
    order_pay as account_pay,
    get_order_items_list_by_order_id as get_items_by_account_id,
)
# from bot.services import notification_service as notify
from app.models import Order as Account
from payment.services.payme.subscribe_api import (
    receipts_create_api as get_payme_invoice_id,
    receipts_cancel_api as cancel_payme_payment
    )
from payment.services.click import get_click_invoice_url
from payment.models import Payme_transaction



async def get_invoice_url(payment_id, amount, payment_system):
    if str(payment_system).lower() == 'payme':
        # create receipt
        invoice_id = await get_payme_invoice_id(payment_id, amount)
        url = f'https://payme.uz/checkout/{invoice_id}'
    if str(payment_system).lower() == 'click':
        url = get_click_invoice_url(payment_id, amount)
    # if payment_system == 'Uzum':
    #     url = get_uzum_invoice_url(payment_id, amount)
    return url


async def cancel_order_payment(order: Account) -> str:
    """
    Cancels the specified order associated with the given account.

    Args:
        order (Order): The app.Order object representing the order to be canceled.

    Returns:
        str: A string indicating the result of the operation. 
             Possible values are 'success' if the order was canceled successfully, 
             or 'error' if the cancellation failed.
    """

    if str(order.payment_system).lower() == "payme":
        receipt = await Payme_transaction.objects.aget(order_id=order.id)
        response = await cancel_payme_payment(receipt.payme_trans_id)
        result = response.get("result", None)
        return "success" if result else "error"
