from payment.models import Click_transaction
from app.models import Order


def get_or_create_click_transaction(
        order: Order, click_trans_id: str, click_paydoc_id: int, 
        amount: int, sign_time: str
        ) -> Click_transaction:
    click_transaction, created = Click_transaction.objects.get_or_create(
        click_paydoc_id=click_paydoc_id,
        defaults={
            'click_trans_id': click_trans_id,
            'order': order,
            'amount': amount,
            'sign_time': sign_time
        }
    )
    return click_transaction

def get_click_transaction(click_paydoc_id: int = None, order: Order = None) -> Click_transaction:
    if click_paydoc_id:
        return Click_transaction.objects.get(click_paydoc_id=click_paydoc_id)
    elif order:
        return Click_transaction.objects.get(order=order)
    return None
