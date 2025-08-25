from payment.services import *
from payment.resources.payme_responses import Errors, Results
from payment.utils import time_ts
from payment.services.payme.transaction import *
import logging
from bot.control.updater import application


async def CheckPerformTransaction(amount, account_id, test):
    if account := await get_account_by_id(account_id):
        if trans_obj := await get_active_transaction_by_account_id(account_id):
            return None, Errors.ACCOUNT_NOT_FOUND
        if int(amount) / 100 != int(account.total):
            return None, Errors.INCORRECT_AMOUNT
        account: Account
        items = await get_items_by_account_id(account.id)
        return await Results.CHECKPERFORM_TRANSACTION(account, items, test), None
    else:
        return None, Errors.ACCOUNT_NOT_FOUND


async def CreateTransaction(id, time, amount, account_id, test):
    if account := await get_account_by_id(account_id):
        if await time_ts() - time >= 43200000:
            return {}, Errors.CANNOT_PERFORM_OPERATION
        if trans_obj := await get_active_transaction_by_account_id(account_id):
            trans_obj: Trans
            if trans_obj.payme_trans_id != id:
                return None, Errors.ACCOUNT_NOT_FOUND
        if int(amount) / 100 != int(account.total):
            return None, Errors.INCORRECT_AMOUNT
        trans_obj = await get_or_create_transaction(
            id, account, amount/100, await time_ts(), time, test)
        create_time = trans_obj.create_time
        trans_id = str(trans_obj.id)
        state = trans_obj.state
        return await Results.CREATE_TRANSACTION(create_time, trans_id, state), None
    else:
        return None, Errors.ACCOUNT_NOT_FOUND


async def PerformTransaction(id):
    if trans_obj := await get_transaction_by_payme_trans_id(id):
        trans_obj: Trans
        # check transactio  status
        if trans_obj.state == 1:
            # check time out
            if await time_ts() - trans_obj.create_time >= 43200000:
                await cancel_transaction(trans_obj, -1, 4)
                return {}, Errors.CANNOT_PERFORM_OPERATION
            # change account status
            try:
                # change account status as payed
                account_id = trans_obj.account_id
                account: Account = await get_account_by_id(account_id)
                if account.payed:
                    assert False
                # send notification to user
                await account_pay(account, 'payme')

            except Exception as ex:
                logging.error("Exception while succesfully payment:", ex)
                await cancel_transaction(trans_obj, -1, 10)
                return None, Errors.CANNOT_PERFORM_OPERATION
            # end transaction
            await perform_transaction(trans_obj)
        else:
            if trans_obj.state != 2:
                return None, Errors.CANNOT_PERFORM_OPERATION

        # success return
        trans_id = str(trans_obj.id)
        perform_time = trans_obj.perform_time
        state = trans_obj.state
        return await Results.PERFORM_TRANSACTION(trans_id, perform_time, state), None
    else:
        return None, Errors.TRANSACTION_NOT_FOUND


async def CancelTransaction(id, reason):
    if trans_obj := await get_transaction_by_payme_trans_id(id):
        trans_obj: Trans
        if trans_obj.state == 1:
            await cancel_transaction(trans_obj, -1, reason)
        elif trans_obj.state == 2:
            await cancel_transaction(trans_obj, -2, reason)
            # return None, Errors.CANNOT_CANCEL_TRANSACTION
        # success return
        trans_id = str(trans_obj.id)
        cancel_time = trans_obj.cancel_time
        state = trans_obj.state
        return await Results.CANCEL_TRANSACTION(trans_id, cancel_time, state), None
    else:
        return None, Errors.TRANSACTION_NOT_FOUND


async def CheckTransaction(id):
    if trans_obj := await get_transaction_by_payme_trans_id(id):
        trans_obj: Trans
        result = await Results.CHECK_TRANSACTION(
            trans_obj.create_time, trans_obj.perform_time,
            trans_obj.cancel_time, str(trans_obj.id),
            trans_obj.state, trans_obj.reason
        )
        return result, None
    else:
        return None, Errors.TRANSACTION_NOT_FOUND


async def GetStatement(from_, to):
    transactions = await filter_transactions_by_createtime_period(from_, to)
    return await Results.GET_STATEMENT(transactions), None
