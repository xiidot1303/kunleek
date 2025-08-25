from django.urls import path
from payment.views import (
    payme, click
)

urlpatterns = [
    # Payme
    path('payme/endpoint', payme.Endpoint.as_view()),

    # Click
    path('click/prepare', click.Prepare.as_view()),
    path('click/complete', click.Complete.as_view()),
]