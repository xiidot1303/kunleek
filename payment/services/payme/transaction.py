from app.services import *
from payment.services import *
from payment.models import Payme_transaction as Trans
from payment.utils import time_ts


async def get_or_create_transaction(
        payme_trans_id, account: Account,
        amount, time, create_time, test) -> Trans:
    obj, created = await Trans.objects.aget_or_create(payme_trans_id=payme_trans_id)
    if created:
        obj.account_id = account.id
        obj.amount = amount
        obj.time = time
        obj.create_time = create_time
        obj.state = 1
        obj.test = test
        await obj.asave()
    return obj


async def get_transaction_by_payme_trans_id(id):
    try:
        obj = await Trans.objects.aget(payme_trans_id=id)
        return obj
    except:
        return None


async def get_active_transaction_by_account_id(account_id):
    try:
        obj = await Trans.objects.aget(
            Q(account_id=account_id)
            & (Q(state=1) | Q(state=2)))
        return obj
    except:
        return None


async def perform_transaction(obj: Trans):
    obj.state = 2
    obj.perform_time = await time_ts()
    await obj.asave()
    return


async def cancel_transaction(obj: Trans, state: int, reason: int):
    obj.state = state
    obj.reason = reason
    obj.cancel_time = await time_ts()
    await obj.asave()
    return


async def filter_transactions_by_createtime_period(from_, to) -> dict:
    filter_dict = {
        "create_time__range": (from_, to),
    }
    return filter_dict
