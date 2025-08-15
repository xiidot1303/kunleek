from rest_framework import viewsets
from bot.models import Bot_user
from app.serializers import BotUserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from app.swagger_schemas import *
from app.services.billz_service import *



class BotUserViewSet(viewsets.ModelViewSet):
    queryset = Bot_user.objects.all()
    serializer_class = BotUserSerializer

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a bot user by user id.
        """
        user_id = kwargs.get('pk')
        try:
            bot_user = self.queryset.get(user_id=user_id)
            serializer = self.get_serializer(bot_user)
            return Response(serializer.data)
        except Bot_user.DoesNotExist:
            return Response({"error": "Bot user not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    

    @swagger_auto_schema(
        method='get',
        manual_parameters=[openapi.Parameter('user_id', openapi.IN_PATH, description="User ID", type=openapi.TYPE_INTEGER)],
        responses={200: openapi.Response('Bot user details', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'balance': openapi.Schema(type=openapi.TYPE_NUMBER, description='User balance')
        }))}
            
    )
    @action(detail=False, methods=['get'], url_path='balance/(?P<user_id>[^/.]+)')
    def get_balance(self, request, user_id=None):
        """
        Get the balance of a bot user.
        """
        try:
            bot_user = self.queryset.get(user_id=user_id)
            # get the balance of the bot user from Billz
            billz_id = bot_user.billz_id
            billz_service = BillzService(APIMethods.customer)
            client_details: ClientDetails = billz_service.get_client_by_id(billz_id)
            if client_details:
                balance = client_details.balance
            else:
                return Response({"error": "Client not found"}, status=404)
            return Response({"balance": balance})
        except Bot_user.DoesNotExist:
            return Response({"error": "Bot user not found"}, status=404)