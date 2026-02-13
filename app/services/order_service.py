from app.models import Order, Product, OrderItem
from celery import shared_task
from app.services.billz_service import BillzService, APIMethods
from asgiref.sync import sync_to_async
from core.exceptions import OrderError, BillzAPIError
import html
from app.utils.data_classes import OrderStatus


@shared_task
def send_order_to_billz(order_id):
    try:
        order = Order.objects.get(id=order_id)
        items = order.items.all()

        billz_service = BillzService(method=APIMethods.create_order)
        billz_service.create_order(
            shop_id=order.shop.shop_id,
            cashbox_id=order.shop.cashbox_id
        )
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
        
        order.billz_id = billz_service.order_number
        order.save(update_fields=["billz_id"])
    except BillzAPIError as e:
        order.status = OrderStatus.ERROR_IN_BILLZ_API
        order.save(update_fields=["status"])
        error = (
            f"<b>Error occurred while sending order to Billz:</b> {e}\n"
            f"ID: {order.id}\n"
            f"URL: <code>{e.url}</code>\n"
            f"Response Data: <pre>{(html.escape(str(e.response_data)))}</pre>"
        )
        raise OrderError(error, order_id=order.id)

async def get_order_by_id(id: int | str) -> Order | None:
    obj = await Order.objects.filter(id=id).afirst()
    return obj


async def order_pay(order: Order, payment_system):
    order.payed = True
    order.payment_system = payment_system
    await order.asave(update_fields=['payed', 'payment_system'])


@sync_to_async
def get_order_items_list_by_order_id(order_id: int | str) -> list | None:
    items = list(OrderItem.objects.filter(order_id=order_id).values(
        'id', 'order_id', 'product_id', 'product__name', 'product__mxik', 'product__package_code', 'quantity', 'price'
    ))
    return items