from app.models import Order, Product, OrderItem
from celery import shared_task
from app.services.billz_service import BillzService, APIMethods
from asgiref.sync import sync_to_async


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

    billz_service.bind_client_to_order(client_id=order.bot_user.billz_id)
    billz_service.complete_order(
        paid_amount=order.subtotal - order.bonus_used, 
        payment_method=order.payment_method,
        with_cashback=order.bonus_used
        )
    

async def get_order_by_id(id: int | str) -> Order | None:
    obj = await Order.objects.filter(id=id).afirst()
    return obj


async def order_pay(order: Order, payment_system):
    order.payed = True
    order.payment_system = payment_system
    await order.asave()


@sync_to_async
def get_order_items_list_by_order_id(order_id: int | str) -> list | None:
    items = list(OrderItem.objects.filter(order_id=order_id).values(
        'id', 'order_id', 'product_id', 'product__name', 'product__mxik', 'product__package_code', 'quantity', 'price'
    ))
    return items