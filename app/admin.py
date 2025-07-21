from django.contrib import admin
from app.models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'billz_id', 'parent_category', 'index')
    search_fields = ('name', 'billz_id')
    list_filter = ('parent_category',)
    ordering = ('index',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'sku')
    search_fields = ('name', 'sku')
    list_filter = ('category',)
    ordering = ('name',)
    list_editable = ('price', 'sku')