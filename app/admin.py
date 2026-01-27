from django.contrib import admin
from app.models import *
from django.urls import path
from django.contrib import messages
from django.shortcuts import redirect
import pandas as pd
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.db import transaction
from django.db.models import F


def fetch_shops_manually(request):
    from app.scheduled_job.billz_job import fetch_shops
    fetch_shops()
    messages.success(request, "Магазины успешно обновлены!")
    return redirect("../")


def fetch_categories_manually(request):
    from app.scheduled_job.billz_job import fetch_categories
    fetch_categories()
    messages.success(request, "Категории успешно обновлены!")
    return redirect("../")


def fetch_products_manually(request):
    from app.scheduled_job.billz_job import fetch_products
    fetch_products()
    messages.success(request, "Продукты успешно обновлены!")
    return redirect("../")


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'is_active')
    search_fields = ('name', 'shop_id', 'cashbox_id')
    list_filter = ('is_active',)
    ordering = ('name',)
    list_editable = ('is_active', 'latitude', 'longitude')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("fetch-shop-manually/", self.admin_site.admin_view(fetch_shops_manually),
                 name="fetch_shops_manually"),
        ]
        return custom_urls + urls
        

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_uz', 'name_ru',
                    'index', 'parent_category', 'photo')
    search_fields = ('name', 'billz_id')
    list_filter = ('parent_category',)
    ordering = ('index',)
    list_editable = ('index', 'name_uz', 'name_ru',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("fetch-categories-manually/", self.admin_site.admin_view(fetch_products_manually),
                 name="fetch_categories_manually"),
        ]
        return custom_urls + urls


class DiscountCategoryProductInline(admin.TabularInline):
    model = Product
    extra = 1


@admin.register(DiscountCategory)
class DiscountCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'index')
    search_fields = ('name',)
    ordering = ('index',)
    list_editable = ('index',)
    inlines = [DiscountCategoryProductInline]


class DiscountedPriceFilter(admin.SimpleListFilter):
    title = "Статус скидки"
    parameter_name = "discounted"

    def lookups(self, request, model_admin):
        return (
            ("discounted_products", "Товары со скидкой"),
        )

    def queryset(self, request, queryset):
        if self.value() == "discounted_products":
            return queryset.filter(price__lt=F("price_without_discount"))
        return queryset


class ProductByShopInline(admin.TabularInline):
    model = ProductByShop
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'discount_category', 'name_uz',
                    'name_ru', 'mxik', 'package_code', 'active')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'active', DiscountedPriceFilter,)
    ordering = ('name',)
    list_editable = ('name_uz', 'name_ru', 'mxik', 'package_code', 'active')
    change_list_template = "admin/app/product/change_list.html"
    inlines = [ProductByShopInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("fetch-products-manually/", self.admin_site.admin_view(fetch_products_manually),
                 name="fetch_products_manually"),
            path(
                "upload-sku-excel/",
                self.admin_site.admin_view(self.upload_sku_excel),
                name="product-upload-sku-excel",
            )
        ]
        return custom_urls + urls

    def upload_sku_excel(self, request):
        if request.method == "POST":
            excel_file = request.FILES.get("file")

            if not excel_file:
                self.message_user(request, "No file uploaded",
                                  level=messages.ERROR)
                return redirect("..")

            try:
                # Read Excel, no header assumption
                df = pd.read_excel(excel_file, dtype=str)
                # Normalize headers
                df.columns = [str(c).strip().lower() for c in df.columns]

                # Normalize values
                for col in ['sku', 'mxik', 'package_code']:
                    df[col] = df[col].apply(lambda x: str(x).strip() if x not in [None, ''] else None)

                # Remove empty SKUs
                df = df[df['sku'].notna()]

                # Resolve duplicates (keep last)
                df = (
                    df.groupby('sku', as_index=False)
                      .last()
                )

                excel_data = df.set_index('sku').to_dict(orient='index')
                sku_list = list(excel_data.keys())

                # 3. Fetch products in one query
                products = Product.objects.filter(sku__in=sku_list)

                products_to_update = []

                for product in products:
                    data = excel_data.get(product.sku)
                    if not data:
                        continue
                    
                    product.mxik = data.get('mxik')
                    product.package_code = data.get('package_code')
                    product.active = True
                    products_to_update.append(product)

                # 4. Bulk update
                if products_to_update:
                    with transaction.atomic():
                        Product.objects.bulk_update(
                            products_to_update,
                            ['mxik', 'package_code', 'active'],
                            batch_size=1000
                        )
                        Product.objects.exclude(sku__in=sku_list).update(active=False)
                updated_count = len(products_to_update)
                self.message_user(
                    request,
                    f"{updated_count} products marked as active",
                    level=messages.SUCCESS,
                )

            except Exception as e:
                self.message_user(
                    request,
                    f"Error processing file: {e}",
                    level=messages.ERROR,
                )

            return redirect("..")

        return render(request, "admin/upload_sku_excel.html")


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'title_ru', 'price', 'min_order_price', 'free_delivery_order_price')
    search_fields = ('title_uz', 'title_ru')
    ordering = ('title_uz',)
    list_editable = ('price', 'min_order_price', 'free_delivery_order_price')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('photo',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'bot_user', 'customer', 'delivery_type',
                    'payment_method', 'subtotal', 'delivery_price', 'total', 'created_at')
    search_fields = ('customer__first_name',
                     'delivery_type__title_en', 'payment_method')
    list_filter = ('delivery_type', 'payment_method', 'created_at')
    inlines = [OrderItemInline]


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__name', 'product__name')
    list_filter = ('user',)
    ordering = ('user',)


@admin.register(YandexTrip)
class YandexTripAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'claim_id',
        'courier_name',
        'car_model',
        'car_number',
        'status',
    )
    search_fields = (
        'claim_id',
        'courier_name',
        'car_model',
        'car_number',
        'order__id',
    )
    list_filter = ('status',)
