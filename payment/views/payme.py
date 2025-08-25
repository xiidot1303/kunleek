from app.views import *
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from adrf.views import APIView
from adrf.requests import AsyncRequest
from payment.resources.payme_responses import *
from payment.resources import payme_ips
from payment.utils import *
from payment.services.payme.merchant import *
from config import PAYME_KEY, PAYME_TEST_KEY


class Endpoint(APIView):
    authentication_classes = []
    async def set_data(self, request: AsyncRequest):
        self.data: dict = request.data
        self.request_headers = request.headers
        self.id = self.data["id"]
        self.error = None
        self.result = None
        self.auth = request.META["HTTP_AUTHORIZATION"]

    async def check_authorization(self):
        login, password = await get_login_password_from_auth(self.auth)
        if (
            self.request_headers["X-Forwarded-For"] in payme_ips and
            login == 'Paycom'
        ):
            if password == PAYME_KEY:
                self.test = False
            elif password == PAYME_TEST_KEY:
                self.test = True
            else:
                self.error = Errors.NOT_ENOUGH_PRIVILEGES
        else:
            self.error = Errors.NOT_ENOUGH_PRIVILEGES

    async def body(self):
        # get values
        method = self.data["method"]
        params = self.data["params"]
        # check method and create response
        if method == "CheckPerformTransaction":
            amount, account_id = params["amount"], params["account"]["account_id"]
            result, error = await CheckPerformTransaction(
                amount, account_id, self.test)
        if method == "CreateTransaction":
            payme_trans_id = params["id"]
            time = params["time"]
            amount = params["amount"]
            account_id = params["account"]["account_id"]
            result, error = await CreateTransaction(
                payme_trans_id, time, amount, account_id, self.test)
        if method == "PerformTransaction":
            payme_trans_id = params["id"]
            result, error = await PerformTransaction(payme_trans_id)
        if method == "CancelTransaction":
            payme_trans_id = params["id"]
            reason = params["reason"]
            result, error = await CancelTransaction(
                payme_trans_id, reason)
        if method == "CheckTransaction":
            payme_trans_id = params["id"]
            result, error = await CheckTransaction(payme_trans_id)
        if method == "GetStatement":
            from_, to = params["from"], params["to"]
            result, error = await GetStatement(from_, to)
        self.result, self.error = result, error

    async def create_response(self):
        response_data = {
            "jsonrpc": "2.0",
            "id": self.id
        }
        if self.error:
            response_data["error"] = self.error
        else:
            response_data["result"] = self.result
        response = JsonResponse(response_data)
        response['Content-Type'] = 'application/json'
        response['charset'] = 'UTF-8'
        return response

    async def get(self, request: AsyncRequest, *args, **kwargs):
        self.error = Errors.REQUEST_IS_NOT_POST
        self.id = None
        return await self.create_response()

    async def post(self, request: AsyncRequest, *args, **kwargs):
        try:
            # make ready
            await self.set_data(request)
            # check Authorization
            await self.check_authorization()
            # BODY
            if not self.error:
                await self.body()
        except Exception as ex:
            print("Exception: ", ex)
            self.error = Errors.NOT_ENOUGH_PRIVILEGES

        return await self.create_response()
