from config import *

def get_click_invoice_url(paymend_id, amount):
    url = 'https://my.click.uz/services/pay?service_id={service_id}&merchant_id={merchant_id}&amount={amount}&transaction_param={transaction_param}'
    url = url.format(
        service_id = CLICK_SERVICE_ID,
        merchant_id = CLICK_MERCHANT_ID,
        amount = amount,
        transaction_param = paymend_id
    )
    return url