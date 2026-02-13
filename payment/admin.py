from django.contrib import admin
from payment.models import *


class Payme_transactionAdmin(admin.ModelAdmin):
    list_display = ['payme_trans_id', 'amount', 'create_time', 'state', 'test']


class PaymeTransactionInline(admin.TabularInline):
    model = Payme_transaction
    extra = 0
    can_delete = False
    verbose_name_plural = "оплаты Payme"

class ClickTransactionInline(admin.TabularInline):
    model = Click_transaction
    extra = 0
    can_delete = False
    verbose_name_plural = "оплаты Click"

admin.site.register(Payme_transaction, Payme_transactionAdmin)
