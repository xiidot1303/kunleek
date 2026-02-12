from bot.bot import *
from app.models import Order, OrderStatus


async def confirm_order(update: Update, context: CustomContext):
    query = update.callback_query
    await query.answer("✅ Заказ подтвержден.")

    data = query.data
    _, order_id = data.split("-")

    order = await Order.objects.aget(id=order_id)
    order.status = OrderStatus.READY_TO_APPROVAL
    await order.asave(update_fields=['status'])
    await query.delete_message()


async def order_delivered(update: Update, context: CustomContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    _, order_id = data.split("-")

    order = await Order.objects.aget(id=order_id)
    order.status = OrderStatus.DELIVERED
    await order.asave(update_fields=["status"])
    await query.edit_message_reply_markup()