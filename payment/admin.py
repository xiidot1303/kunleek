from django.contrib import admin
from payment.models import *


class Payme_transactionAdmin(admin.ModelAdmin):
    list_display = ['payme_trans_id', 'amount', 'create_time', 'state', 'test']


admin.site.register(Payme_transaction, Payme_transactionAdmin)
