from rest_framework import viewsets
from rest_framework.response import Response
from app.models import DeliveryType
from app.serializers import DeliveryTypeSerializer
from django.db.models import F, Case, When, TextField
from app.swagger_schemas import *
from datetime import datetime
from app.utils import weekdays_by_lang


class DeliveryTypeViewSet(viewsets.ModelViewSet):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lang = self.request.GET.get("lang", "ru")
        # `lang` is a request variable, not a model field. Choose an available
        # description field based on the lang parameter. If model doesn't have
        # localized description fields, fall back to the generic `description`.
        desc_field = f"description_{lang}"
        queryset = queryset.annotate(description=F(desc_field))

        return queryset

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('lang', openapi.IN_QUERY, description="Language code", type=openapi.TYPE_STRING)
    ])
    def list(self, request, *args, **kwargs):
        """Return delivery types, replacing description with out_of_work_message when closed."""
        lang = request.GET.get('lang', 'ru')

        queryset = self.filter_queryset(self.get_queryset())
        # evaluate queryset to preserve instance order for parallel processing
        instances = list(queryset)
        serializer = self.get_serializer(instances, many=True)
        data = list(serializer.data)

        # replace description per-instance when out of working hours
        for idx, inst in enumerate(instances):
            inst: DeliveryType
            try:
                open_now = inst.is_open()
            except Exception:
                open_now = True

            if not open_now:
                msg_field = f"out_of_work_message_{lang}"
                msg = getattr(inst, msg_field, None)
                next_work_datetime: datetime = inst.next_work_day()
                msg = msg.format(
                    next_work_date=next_work_datetime.strftime("%d.%m.%Y"),
                    next_work_time=inst.work_start_time.strftime("%H:%M"),
                    next_work_weekday=weekdays_by_lang[lang][next_work_datetime.weekday()],
                )
                if msg:
                    data[idx]['description'] = msg

        return Response(data)
