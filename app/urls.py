from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import (
    LoginView, 
    LogoutView, 
    PasswordChangeDoneView, 
    PasswordChangeView
)
from app.views import main
from app.views.product import ProductViewSet
from app.views.category import CategoryViewSet
from app.views.delivery import DeliveryTypeViewSet
from app.views.banner import BannerViewSet
from app.views.shop import ShopViewSet
from app.views.order import OrderViewSet, OrderItemViewSet
from app.views.favorite_product import FavoriteProductViewSet
from app.views.client import BotUserViewSet
from app.views.yandex_delivery import YandexDeliveryView, CheckPrice


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'shops', ShopViewSet, basename='shop')
router.register(r'delivery-types', DeliveryTypeViewSet, basename='delivery-type')
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'favorite-products', FavoriteProductViewSet, basename='favoriteproduct')
router.register(r'bot-users', BotUserViewSet, basename='botuser')

# Swagger imports
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Store API",
        default_version='v1',
        description="API documentation for Product and Category",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', main.main),
    # login
    path('accounts/login/', LoginView.as_view()),
    path('changepassword/', PasswordChangeView.as_view(
        template_name = 'registration/change_password.html'), name='editpassword'),
    path('changepassword/done/', PasswordChangeDoneView.as_view(
        template_name = 'registration/afterchanging.html'), name='password_change_done'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # files
    re_path(r'^files/(?P<path>.*)$', main.get_file),

    # API
    path('api/', include(router.urls)),

    # Swagger/OpenAPI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('yandex-delivery-callback', YandexDeliveryView.as_view(), name='yandex-delivery-callback'),
    path('yandex-delivery-check-price', CheckPrice.as_view(), name='yandex-delivery-check-price'),
]
