from django.contrib import admin
from app.models import *
from django import forms
from django.urls import path
from django.contrib import messages
from django.shortcuts import redirect
import pandas as pd
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.db import transaction
from django.db.models import F
from import_export import resources, fields
from import_export.admin import ExportMixin
from payment.admin import PaymeTransactionInline, ClickTransactionInline


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
    list_display = ('name', 'address', 'phone', 'latitude', 'longitude', 'tg_group_id', 'is_active')
    search_fields = ('name', 'shop_id', 'cashbox_id')
    list_filter = ('is_active',)
    ordering = ('name',)
    list_editable = ('is_active', 'latitude', 'longitude', 'address', 'tg_group_id', 'phone')

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
    list_filter = ('category', 'active')
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


@admin.register(ProductByShop)
class ProductByShopAdmin(admin.ModelAdmin):
    list_display = ('shop', 'product', 'product_category',
                    'product_discount_category', 'price', 'price_without_discount', 'quantity')
    search_fields = ('shop__name', 'product__name')
    list_filter = ('shop', 'product', DiscountedPriceFilter)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            .select_related('shop', 'product')
            .annotate(
                product_category=F('product__category__name'),
                product_discount_category=F('product__discount_category__name'),
            )
        )

    @admin.display(
        description='Category',
        ordering='product_category',
    )
    def product_category(self, obj):
        return obj.product_category

    @admin.display(
        description='Discount Category',
        ordering='product_discount_category',
    )
    def product_discount_category(self, obj):
        return obj.product_discount_category


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'title_ru', 'price', 'min_order_price', 'free_delivery_order_price')
    search_fields = ('title_uz', 'title_ru')
    ordering = ('title_uz',)
    list_editable = ('price', 'min_order_price', 'free_delivery_order_price')


WEEKDAY_CHOICES = [
    ('0', 'Понедельник'),
    ('1', 'Вторник'),
    ('2', 'Среда'),
    ('3', 'Четверг'),
    ('4', 'Пятница'),
    ('5', 'Суббота'),
    ('6', 'Воскресенье'),
]


class DeliveryTypeForm(forms.ModelForm):
    working_days = forms.MultipleChoiceField(
        choices=WEEKDAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Рабочие дни",
        help_text="Выберите рабочие дни 0=Понедельник..6=Воскресенье",
    )

    class Meta:
        model = DeliveryType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # populate initial values from instance (convert ints to strings)
        if self.instance and getattr(self.instance, 'working_days', None):
            self.initial['working_days'] = [str(d) for d in self.instance.working_days]

        # Explain available placeholders for out-of-work messages
        placeholder_help = (
            "Допустимы плейсхолдеры: {next_work_date}, {next_work_time}, {next_work_weekday}. "
            "Они будут заменены на ближайшую дату/время/день недели, когда доставка снова будет доступна. "
            "Пример: 'Открываем {next_work_time} {next_work_date} ({next_work_weekday})'."
        )

        for fld in ('out_of_work_message_uz', 'out_of_work_message_ru'):
            if fld in self.fields:
                # append to existing help_text if present
                existing = self.fields[fld].help_text or ''
                if existing:
                    self.fields[fld].help_text = f"{existing} {placeholder_help}"
                else:
                    self.fields[fld].help_text = placeholder_help
                # also set a small placeholder in the textarea widget if possible
                widget = self.fields[fld].widget
                try:
                    widget.attrs.setdefault('placeholder', 'Используйте плейсхолдеры, например: {next_work_time} {next_work_date}')
                except Exception:
                    pass

    def clean_working_days(self):
        val = self.cleaned_data.get('working_days') or []
        # convert to ints before saving to JSONField
        return [int(x) for x in val]


# attach the custom form to the admin
DeliveryTypeAdmin.form = DeliveryTypeForm


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('photo',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderReviewInline(admin.TabularInline):
    model = OrderReview
    extra = 1


class OrderResource(resources.ModelResource):
    items = fields.Field()
    reviews = fields.Field()
    shop = fields.Field(attribute='shop__name')
    delivery_type = fields.Field(attribute='delivery_type__title_ru')
    bot_user = fields.Field(attribute='bot_user__name')
    customer = fields.Field(attribute='customer__first_name')

    def dehydrate_items(self, order):
        return "\n".join(
            f"{i.product_name} x{i.quantity} | {i.price}"
            for i in order.items.all()
        )

    def dehydrate_reviews(self, order):
        return "\n".join(
            f"{r.rating} | {r.comment}"
            for r in order.reviews.all()
        )
    class Meta:
        model = Order

@admin.register(Order)
class OrderAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = OrderResource
    list_display = ('billz_id', 'shop', 'bot_user', 'customer', 'delivery_type',
                    'payment_method', 'delivery_price', 'total', 'status', 'created_at')
    search_fields = ('customer__first_name',
                     'delivery_type__title_en', 'payment_method')
    list_filter = ('delivery_type', 'payment_method', 'created_at', 'shop')
    inlines = [OrderItemInline, OrderReviewInline, PaymeTransactionInline, ClickTransactionInline]


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


@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'comment')
    search_fields = ('order__id', 'comment')
    list_filter = ('rating',)