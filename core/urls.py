from django.contrib import admin
from django.urls import path, include
import debug_toolbar

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path('xiidot1303/', admin.site.urls),
    path('', include('app.urls')),
    path('', include('bot.urls')),
    path('payment/', include('payment.urls')),
]
