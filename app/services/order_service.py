from app.models import Order, Product, OrderItem, ProductByShop, BillzOrder
from celery import shared_task
from app.services.billz_service import BillzService, APIMethods
from asgiref.sync import sync_to_async
from core.exceptions import OrderError, BillzAPIError
import html
from app.utils.data_classes import OrderStatus
from app.services.product_service import update_filtered_product_quantity_from_billz
from asgiref.sync import sync_to_async
from app.services.error_handler import run_on_error


@shared_task
def send_order_to_billz(order_id, created_order_id: str | None = None):
    try:
        order = Order.objects.get(id=order_id)
        payed_amount = order.subtotal - order.bonus_used - order.discount_amount
        billz_service = BillzService(method=APIMethods.create_order)
        if not created_order_id:

            items = order.items.all()
            billz_service.create_order(
                shop_id=order.shop.shop_id,
                cashbox_id=order.shop.cashbox_id
            )
            # add products to the order
            for item in items:
                item: OrderItem
                product_by_shop = ProductByShop.objects.get(product=item.product, shop=order.shop)
                bot_price = product_by_shop.price
                billz_price = product_by_shop.original_price
                if bot_price != billz_price:
                    is_manual = True
                    free_price = int(bot_price)
                else:
                    is_manual = False
                    free_price = None

                billz_service.add_product_to_order(
                    product_id=item.product.billz_id,
                    quantity=item.quantity,
                    is_manual=is_manual,
                    free_price=free_price
                )

            billz_service.bind_client_to_order(client_id=order.bot_user.billz_id)
            if order.discount_amount:
                billz_service.make_discount(amount=payed_amount)
            BillzOrder.objects.create(
                order=order,
                billz_id=billz_service.order_id,
            )
            order.billz_id = billz_service.order_number
            order.save(update_fields=["billz_id"])
            return
        else:
            billz_service.order_id = created_order_id
            billz_service.complete_order(
                paid_amount=payed_amount, 
                payment_method=order.payment_method,
                with_cashback=order.bonus_used
            )
    except BillzAPIError as e:
        order.status = OrderStatus.ERROR_IN_BILLZ_API
        order.billz_id = None

        order.save(update_fields=["status", "billz_id"])
        error = (
            f"<b>Error occurred while sending order to Billz:</b> {e}\n"
            f"ID: {order.id}\n"
            f"URL: <code>{e.url}</code>\n"
            f"Response Data: <pre>{(html.escape(str(e.response_data)))}</pre>"
        )
        raise OrderError(error, order_id=order.id)


def check_order_items_availability_from_billz(order: Order) -> list:
    """
    Returns product names list that not available
    """
    # update order products from Billz before
    order_items = OrderItem.objects.filter(order_id=order.pk)
    product_skus = list(order_items.values_list(
        "product__sku", flat=True
    ))

    billz_service = BillzService(method=APIMethods.products_with_filter)
    products = billz_service.fetch_products_with_filters(skus=product_skus, shop_ids=[order.shop.shop_id])
    if products:
        update_filtered_product_quantity_from_billz(products, order.shop.pk, product_skus)
    

    # check order items quantity from product by shops
    products_by_shop_and_product = {}
    for pb in ProductByShop.objects.filter(product__sku__in=product_skus, shop_id=order.shop.pk).select_related('product'):
        products_by_shop_and_product[pb.product.pk] = pb
    
    products_not_available: list[str] = []
    for order_item in order_items:
        pb: ProductByShop = products_by_shop_and_product[order_item.product.pk]
        if order_item.quantity > pb.quantity:
            products_not_available.append(pb.product.name_ru or pb.product.name)
    
    return products_not_available




async def get_order_by_id(id: int | str) -> Order | None:
    obj = await Order.objects.filter(id=id).afirst()
    return obj


async def order_pay(order: Order, payment_system):
    try:
        billz_order = await BillzOrder.objects.filter(order_id=order.pk).alast()
        await sync_to_async(send_order_to_billz)(order.pk , billz_order.billz_id)
        order.payed = True
        order.payment_system = payment_system
        await order.asave(update_fields=['payed', 'payment_system'])
    except OrderError as e:
        # send to admin
        await sync_to_async(run_on_error)(e)
        raise e


def get_order_items_list_by_order_id(order_id: int | str) -> list | None:
    items = list(OrderItem.objects.filter(order_id=order_id).values(
        'id', 'order_id', 'product_id', 'product__name', 'product__mxik', 'product__package_code', 'quantity', 'price'
    ))
    return items