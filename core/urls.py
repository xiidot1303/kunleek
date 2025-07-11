from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('xiidot1303/', admin.site.urls),
    path('', include('app.urls')),
    path('', include('bot.urls')),
]
