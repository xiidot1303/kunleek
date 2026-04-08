from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from app.models import PromoCode
from app.serializers import PromoCodeSerializer
from app.services.promocode_service import get_valid_promo_code
from app.swagger_schemas import *
from bot.models import Bot_user
from bot.resources.strings import Strings


class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer

    @swagger_auto_schema(
        method='get',
        manual_parameters=[promocode_param, user_id_param, lang_param],
        responses={
            200: openapi.Response('Valid promo code', PromoCodeSerializer),
            400: openapi.Response('Code parameter is required or Promo code already used by this user', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
            404: openapi.Response('Invalid or expired promo code or User not found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}))
        }
    )
    @action(detail=False, methods=['get'], url_path='validate')
    def validate_code(self, request: Request):
        code = request.query_params.get('code')
        user_id = request.query_params.get('user_id')
        lang = request.query_params.get('lang')
        lang_code = 0 if lang == 'uz' else 1
        if not code:
            return Response({'error': 'Code parameter is required'}, status=400)

        promo_code: PromoCode | None = get_valid_promo_code(code)
        if promo_code:
            # check this promo code is already used by this user
            bot_user = Bot_user.objects.filter(user_id=user_id).first()
            if not bot_user:
                return Response({'error': 'User not found'}, status=404)
            if promo_code.used_by.filter(id=bot_user.id).exists():
                return Response({'error': Strings.promocode_already_used[lang_code]}, status=400)
            serializer = self.get_serializer(promo_code)
            return Response(serializer.data)
        return Response({'error': Strings.invalid_promocode[lang_code]}, status=404)