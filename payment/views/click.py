from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from payment.utils import click_utils
from adrf.views import APIView
from adrf.requests import AsyncRequest
from asgiref.sync import sync_to_async


class Prepare(APIView):
    async def post(self, request: AsyncRequest, *args, **kwargs):
        return await sync_to_async(click_utils.prepare)(request)


class Complete(APIView):
    async def post(self, request: AsyncRequest, *args, **kwargs):
        return await sync_to_async(click_utils.complete)(request)
