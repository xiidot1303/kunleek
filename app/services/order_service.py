from app.models import Order, Product, OrderItem
from celery import shared_task
from app.services.billz_service import BillzService, APIMethods


@shared_task
def send_order_to_billz(order_id):
    order = Order.objects.get(id=order_id)
    items = order.items.all()

    billz_service = BillzService(method=APIMethods.create_order)
    billz_service.create_order()
    # add products to the order
    for item in items:
        item: OrderItem
        billz_service.add_product_to_order(
            product_id=item.product.billz_id,
            quantity=item.quantity
        )
    if order.bonus_used:
        billz_service.make_discount(amount=order.bonus_used)

    billz_service.bind_client_to_order(client_id=order.bot_user.billz_id)
    billz_service.complete_order(paid_amount=order.total, payment_method=order.payment_method)