from django.contrib import admin
from app.models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_uz', 'name_ru', 'index', 'parent_category', 'photo')
    search_fields = ('name', 'billz_id')
    list_filter = ('parent_category',)
    ordering = ('index',)
    list_editable = ('index', 'name_uz', 'name_ru',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'name_uz', 'name_ru', 'mxik', 'package_code')
    search_fields = ('name', 'sku')
    list_filter = ('category',)
    ordering = ('name',)
    list_editable = ('name_uz', 'name_ru', 'mxik', 'package_code')

@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'title_ru', 'price')
    search_fields = ('title_uz', 'title_ru')
    ordering = ('title_uz',)
    list_editable = ('price',)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('photo',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'bot_user', 'customer', 'delivery_type', 'payment_method', 'subtotal', 'delivery_price', 'total', 'created_at')
    search_fields = ('customer__first_name', 'delivery_type__title_en', 'payment_method')
    list_filter = ('delivery_type', 'payment_method', 'created_at')
    inlines = [OrderItemInline]


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__name', 'product__name')
    list_filter = ('user',)
    ordering = ('user',)

