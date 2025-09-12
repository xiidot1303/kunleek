class Errors:
    ACCOUNT_NOT_FOUND = {
        "code": -31050,
        "message": {
            "ru": "ID не найден",
            "uz": "ID ro'yhatda yo'q",
            "en": "ID not found",
        }
    }

    INCORRECT_AMOUNT = {
        "code": -31001,
        "message": {
            "ru": "Неверная сумма.",
            "uz": "Noto'gri summa.",
            "en": "Incorrect amount."
        }
    }

    TRANSACTION_NOT_FOUND = {
        "code": -31003,
        "message": {
            "ru": "Транзакция не найдена.",
            "uz": "Транзакция не найдена.",
            "en": "Транзакция не найдена."
        }
    }

    CANNOT_PERFORM_OPERATION = {
        "code": -31008,
        "message": {
            "ru": "Невозможно выполнить данную операцию.",
            "uz": "Невозможно выполнить данную операцию.",
            "en": "Невозможно выполнить данную операцию."
        }
    }

    CANNOT_CANCEL_TRANSACTION = {
        "code": -31007,
        "message": {
            "ru": "Заказ выполнен. Невозможно отменить транзакцию.",
            "uz": "Заказ выполнен. Невозможно отменить транзакцию.",
            "en": "Заказ выполнен. Невозможно отменить транзакцию.",
        }
    }

    INCORRECT_TIME = {
        "code": -31060,
        "message": {
            "ru": "incorrect time",
            "uz": "incorrect time",
            "en": "incorrect time",
        }
    }

    NOT_ENOUGH_PRIVILEGES = {
        "code": -32504,
        "message": {
            "ru": "Недостаточно привилегий для выполнения метода.",
            "uz": "Недостаточно привилегий для выполнения метода.",
            "en": "Недостаточно привилегий для выполнения метода.",
        }
    }

    REQUEST_IS_NOT_POST = {
        "code": -32300,
        "message": {
            "ru": "Request method is not POST.",
            "uz": "Request method is not POST.",
            "en": "Request method is not POST.",
        }
    }


class Results:
    async def CHECKPERFORM_TRANSACTION(account, items: list, test=False):
        r = {
            "allow": True,
            "detail": {
                "receipt_type": 0,
                "shipping": {  # доставка, необязательное поле
                    "title": "Доставка",
                    "price": int(account.delivery_price)*100
                },
                "items": [  # товарная позиция, обязательное поле для фискализации
                    {
                        # нааименование товара или услуги
                        "title": item.get("product__name"),
                        # цена за единицу товара или услуги, сумма указана в тийинах
                        "price": int(item.get("price"))*100,
                        # кол-во товаров или услуг
                        "count": item.get("quantity"),
                        # код * ИКПУ обязательное поле
                        "code": item.get("product__mxik"),
                        # обязательное поле, процент уплачиваемого НДС для данного товара или услуги
                        "vat_percent": 0,
                        # Код упаковки для конкретного товара или услуги, содержится на сайте в деталях найденного ИКПУ.
                        "package_code": item.get("product__package_code"),
                    }
                    for item in items
                ]
            }
        }
        # if test:
        #     r.pop('detail')
        return r

    async def CREATE_TRANSACTION(create_time, transaction, state):
        r = {
            "create_time": create_time,
            "transaction": transaction,
            "state": state
        }
        return r

    async def PERFORM_TRANSACTION(transaction, perform_time, state):
        r = {
            "transaction": transaction,
            "perform_time": perform_time,
            "state": state
        }
        return r

    async def CANCEL_TRANSACTION(transaction, cancel_time, state):
        r = {
            "transaction": transaction,
            "cancel_time": cancel_time,
            "state": state
        }
        return r

    async def CHECK_TRANSACTION(create_time, perform_time, cancel_time, transaction, state, reason):
        r = {
            "create_time": create_time,
            "perform_time": perform_time,
            "cancel_time": cancel_time,
            "transaction": transaction,
            "state": state,
            "reason": reason
        }
        return r

    async def GET_STATEMENT(transactions_filter: dict):
        from payment.models import Payme_transaction
        r = {
            "transactions": [
                {
                    "id": transaction.payme_trans_id,
                    "time": transaction.time,
                    "amount": transaction.amount,
                    "account": {
                        "account_id": transaction.account_id
                    },
                    "create_time": transaction.create_time,
                    "perform_time": transaction.perform_time,
                    "cancel_time": transaction.cancel_time,
                    "transaction": str(transaction.id),
                    "state": transaction.state,
                    "reason": transaction.reason,
                    # "receivers" : [
                    # {
                    #     "id" : "5305e3bab097f420a62ced0b",
                    #     "amount" : 200000
                    # },
                    # ]
                }
                async for transaction in Payme_transaction.objects.filter(**transactions_filter)
            ]
        }
        return r
