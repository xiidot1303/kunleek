import requests
from django.utils.translation import gettext_lazy as _
from payments import PaymentStatus
from payments import get_payment_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.conf import settings
import hashlib

from payment.services import *
# from bot.services import notification_service as notify
from adrf.requests import AsyncRequest
from asgiref.sync import async_to_sync


def isset(data, columns):
    for column in columns:
        if data.get(column, None):
            return False
    return True

def order_load(payment_id):
    if int(payment_id) > 1000000000:
        return None
    payment = get_object_or_404(get_payment_model(), id = int(payment_id))
    return payment

def click_secret_key():
    PAYMENT_VARIANTS = settings.PAYMENT_VARIANTS
    _click = PAYMENT_VARIANTS['click']
    secret_key = _click[1]['secret_key']
    return secret_key

def click_webhook_errors(request: AsyncRequest):
    click_trans_id = request.data.get('click_trans_id', None)
    service_id = request.data.get('service_id', None)
    click_paydoc_id = request.data.get('click_paydoc_id', None)
    order_id = request.data.get('merchant_trans_id', None)
    amount = request.data.get('amount', None)
    action = request.data.get('action', None)
    error = request.data.get('error', None)
    error_note = request.data.get('error_note', None)
    sign_time = request.data.get('sign_time', None)
    sign_string = request.data.get('sign_string', None)
    merchant_prepare_id = request.data.get('merchant_prepare_id', None) if action != None and action == '1' else ''

    if isset(request.data, ['click_trans_id', 'service_id', 'click_paydoc_id', 'amount', 'action', 'error', 'error_note', 'sign_time', 'sign_string']) or (
        action == '1' and isset(request.data, ['merchant_prepare_id'])):
        return {
            'error' : '-8',
            'error_note' : _('Error in request from click')
        }
    
    signString = '{}{}{}{}{}{}{}{}'.format(
        click_trans_id, service_id, click_secret_key(), order_id, merchant_prepare_id, amount, action, sign_time
    )
    encoder = hashlib.md5(signString.encode('utf-8'))
    signString = encoder.hexdigest()
    if signString != sign_string:
        return {
            'error' : '-1',
            'error_note' : _('SIGN CHECK FAILED!')
        }
    
    if action not in ['0', '1']:
        return {
            'error' : '-3',
            'error_note' : _('Action not found')
        }
    
    order = order_load(order_id)
    if not order:
        return {
            'error' : '-5',
            'error_note' : _('User does not exist')
        }
        
    if abs(float(amount) - float(order.total)) > 0.01:
        return {
            'error' : '-2',
            'error_note' : _('Incorrect parameter amount')
        }

    if order.status == PaymentStatus.CONFIRMED or order.payed:
        return {
            'error' : '-4',
            'error_note' : _('Already paid')
        }

    

    if action == '1':
        if order_id != merchant_prepare_id:
            return {
                'error' : '-6',
                'error_note' : _('Transaction not found')
            }

    if order.status == PaymentStatus.REJECTED or int(error) < 0:
        return {
            'error' : '-9',
            'error_note' : _('Transaction cancelled')
        }

    return {
        'error' : '0',
        'error_note' : 'Success'
    }

def prepare(request: AsyncRequest):
    order_id = request.data.get('merchant_trans_id', None)
    result = click_webhook_errors(request)
    order = order_load(order_id)
    if result['error'] == '0':
        order.status = PaymentStatus.WAITING
        order.save()
    result['click_trans_id'] = request.data.get('click_trans_id', None)
    result['merchant_trans_id'] = request.data.get('merchant_trans_id', None)
    result['merchant_prepare_id'] = request.data.get('merchant_trans_id', None)
    result['merchant_confirm_id'] = request.data.get('merchant_trans_id', None)
    return JsonResponse(result)

def complete(request: AsyncRequest):
    order_id = request.data.get('merchant_trans_id', None)
    order = order_load(order_id)
    result = click_webhook_errors(request)
    if request.data.get('error', None) != None and int(request.data.get('error', None)) < 0:
        order.status = PaymentStatus.REJECTED
        order.save()
    if result['error'] == '0':
        order.status = PaymentStatus.CONFIRMED
        order.save()
        async_to_sync(account_pay)(order, 'click')

    result['click_trans_id'] = request.data.get('click_trans_id', None)
    result['merchant_trans_id'] = request.data.get('merchant_trans_id', None)
    result['merchant_prepare_id'] = request.data.get('merchant_prepare_id', None)
    result['merchant_confirm_id'] = request.data.get('merchant_prepare_id', None)
    return JsonResponse(result)