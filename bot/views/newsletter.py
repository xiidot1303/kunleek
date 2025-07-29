import json
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from bot.control.updater import application
from telegram import Update
from bot import NewsletterUpdate


@method_decorator(csrf_exempt, name='dispatch')
class NewsletterView(View):
    async def post(self, request: HttpRequest, *args, **kwargs):
        data = json.loads(request.body)
        user_id = data.get('user_id')
        text = data.get('text')

        await application.update_queue.put(NewsletterUpdate(
                    user_id=int(user_id),
                    text=text
                ))
        
        return JsonResponse({"status": "success", "message": "Newsletter sent successfully."})