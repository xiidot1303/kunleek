from django.db import models
from django.utils import timezone
from app.utils.data_classes import *
    

class Shop(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    shop_id = models.CharField(max_length=128, unique=True, verbose_name="ID Магазина Billz")
    cashbox_id = models.CharField(max_length=128, unique=True, verbose_name="ID Кассы Billz")
    # location coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"


class Category(models.Model):
    billz_id = models.CharField(max_length=128, null=True, blank=True, verbose_name="ID Billz")
    name = models.CharField(max_length=100, null=True, unique=True, verbose_name="Название")
    name_uz = models.CharField(max_length=100, blank=True, null=True, verbose_name="Название на узбекском")
    name_ru = models.CharField(max_length=100, blank=True, null=True, verbose_name="Название на русском")
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name="Родительская категория"
    )
    photo = models.FileField(null=True, blank=True, upload_to='category/photos/', verbose_name="Фото")
    index = models.IntegerField(default=0, help_text="Порядок категории в списке")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['index']


class DiscountCategory(models.Model):
    name = models.CharField(max_length=100, null=True, verbose_name="Название")
    index = models.IntegerField(default=0, help_text="Порядок категории в списке")

    class Meta:
        verbose_name = "Скидочная категория"
        verbose_name_plural = "Скидочные категории"
        ordering = ['index']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    discount_category = models.ForeignKey(
        DiscountCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
        verbose_name="Скидочная категория"
    )
    billz_id = models.CharField(max_length=128, unique=True, null=True, verbose_name="ID Billz")
    name = models.CharField(max_length=1024, verbose_name="Название")
    name_uz = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Название на узбекском")
    name_ru = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Название на русском")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    photo = models.URLField(null=True, blank=True, verbose_name="URL фото")
    photos = models.JSONField(
        default=list,
        blank=True,
        help_text="Список URL фото для продукта",
        verbose_name="Фото (список URL)"
    )
    sku = models.CharField(null=True, blank=True, max_length=100, verbose_name="Артикул (SKU)")
    mxik = models.CharField(max_length=100, null=True, blank=True, verbose_name="МХИК")
    package_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="Код упаковки")
    active = models.BooleanField(null=True, default=False)
    
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['name']


class ProductByShop(models.Model):
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='products', verbose_name="Магазин")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shops', verbose_name="Продукт")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    price_without_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена без скидки")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")

    class Meta:
        verbose_name = "Продукт в магазине"
        verbose_name_plural = "Продукты в магазинах"
        unique_together = ('shop', 'product')

    def __str__(self):
        return f"{self.product.name} в {self.shop.name}"


class FavoriteProduct(models.Model):
    user = models.ForeignKey('bot.Bot_user', on_delete=models.CASCADE, related_name='favorite_products', verbose_name="User")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites', verbose_name="Product")
    

class DeliveryType(models.Model):
    title_uz = models.CharField(max_length=255, null=True, verbose_name="Название (узбекский)")
    title_ru = models.CharField(max_length=255, null=True, verbose_name="Название (русский)")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Цена")
    description_uz = models.TextField(null=True, blank=True, verbose_name="Описание (узбекский)")
    description_ru = models.TextField(null=True, blank=True, verbose_name="Описание (русский)")
    TYPE_CHOICES = [
        (DeliveryTypeTitle.ExpressYandex, 'Yandex'),
        (DeliveryTypeTitle.DuringDay, 'В течение дня'),
        (DeliveryTypeTitle.ForTest, 'Тестовая доставка'),
    ]
    type = models.CharField(max_length=100, null=True, choices=TYPE_CHOICES, verbose_name="Тип")
    min_order_price = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Минимальная цена заказа")
    free_delivery_order_price = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Цена бесплатной доставки")
    work_start_time = models.TimeField(null=True, blank=True, verbose_name="Начало рабочего времени")
    work_end_time = models.TimeField(null=True, blank=True, verbose_name="Конец рабочего времени")
    working_days = models.JSONField(default=list, blank=True, verbose_name="Рабочие дни", help_text="Список номеров дней недели 0=Monday..6=Sunday")
    out_of_work_message_uz = models.TextField(null=True, blank=True, verbose_name="Сообщение вне рабочего времени (узбекский)")
    out_of_work_message_ru = models.TextField(null=True, blank=True, verbose_name="Сообщение вне рабочего времени (русский)")

    class Meta:
        verbose_name = "Тип доставки"
        verbose_name_plural = "Типы доставки"

    def __str__(self):
        return self.title_uz

    def is_open(self, dt=None):
        """Return True if the delivery type is available at given datetime (or now).

        - If `working_days` is set (non-empty) it must contain the weekday number (0=Mon..6=Sun).
        - If both `work_start_time` and `work_end_time` are set, the current time must be within the interval.
        If no constraints are set the method returns True.
        """
        if dt is None:
            dt = timezone.datetime.now()

        # check working days
        if self.working_days:
            try:
                day = dt.weekday()
            except Exception:
                return False
            if day not in self.working_days:
                return False

        # check working hours
        if self.work_start_time and self.work_end_time:
            t = dt.time()
            # simple interval check (does not handle overnight ranges)
            return self.work_start_time <= t <= self.work_end_time

        return True

    def next_work_day(self, dt=None) -> timezone.datetime:
        """Return the next working day for this delivery type."""
        if dt is None:
            dt = timezone.datetime.now()

        # Find the next working day
        next_day = dt + timezone.timedelta(days=1)
        while next_day.weekday() not in self.working_days:
            next_day += timezone.timedelta(days=1)

        return next_day


class Banner(models.Model):
    photo = models.FileField(upload_to='banners/', verbose_name="Фото")

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"

    def __str__(self):
        return f"Banner {self.id}"

class Customer(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=255, verbose_name="Адрес")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.first_name


class Order(models.Model):
    billz_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID")
    bot_user = models.ForeignKey('bot.Bot_user', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Пользователь бота")
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE, verbose_name="Клиент")
    shop = models.ForeignKey(Shop, null=True, related_name='orders', on_delete=models.SET_NULL, verbose_name="Магазин")
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name="Тип доставки")
    PAYMENT_METHOD_CHOICES = [
        (PaymentMethod.CASH, 'Наличные'),
        (PaymentMethod.PAYME, 'Payme'),
        (PaymentMethod.CLICK, 'Click')
    ]
    payment_method = models.CharField(max_length=50, verbose_name="Метод оплаты", choices=PAYMENT_METHOD_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена доставки")
    bonus_used = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Использованные бонусы")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая сумма")
    notes = models.TextField(blank=True, null=True, verbose_name="Заметки")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="Адрес доставки")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    payed = models.BooleanField(default=False, verbose_name="Оплачено")
    payment_system = models.CharField(max_length=50, blank=True, null=True, verbose_name="Платежная система")
    STATUS_CHOICES = [
        (OrderStatus.CREATED, 'Создан'),
        (OrderStatus.NEED_CONFIRMATION, 'Нуждается в подтверждении'),
        (OrderStatus.READY_TO_APPROVAL, 'Готов к утверждению'),
        (OrderStatus.WAITING_DELIVERY_WORKING_HOURS, 'Ожидание рабочего времени доставки'),
        (OrderStatus.YANDEX_DELIVERING, 'Yandex Доставляется'),
        (OrderStatus.DELIVERING, 'Доставляется'),
        (OrderStatus.DELIVERED, 'Доставлен'),
        (OrderStatus.RATED, 'Оценен')
    ]
    status = models.CharField(max_length=50, null=True, blank=True, verbose_name="Статус", default=OrderStatus.CREATED, choices=STATUS_CHOICES)
    payment_status = models.CharField(max_length=50, null=True, blank=True, verbose_name="Статус платежа")
    sent_to_group = models.BooleanField(default=False, verbose_name="Отправлено в группу")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order {self.id} by {self.customer.first_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name="Продукт", null=True)
    product_name = models.CharField(max_length=255, verbose_name="Название продукта", null=True, default="")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    def __str__(self):
        return f"{self.product.name}"
    

class OrderReview(models.Model):
    order = models.ForeignKey(Order, related_name='reviews', on_delete=models.CASCADE, verbose_name="Заказ")
    rating = models.PositiveIntegerField(verbose_name="Рейтинг", choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(verbose_name="Комментарий", blank=True)

    class Meta:
        verbose_name = "Отзыв о заказе"
        verbose_name_plural = "Отзывы о заказах"

    def __str__(self):
        return f"Review for Order {self.order.id}"


class YandexTrip(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='yandex_trip', verbose_name="Заказ")
    claim_id = models.CharField(max_length=255, verbose_name="ID поездки Yandex")
    courier_name = models.CharField(null=True, blank=True, max_length=255)
    car_color = models.CharField(null=True, blank=True, max_length=32)
    car_model = models.CharField(null=True, blank=True, max_length=64)
    car_number = models.CharField(null=True, blank=True, max_length=16)
    status = models.CharField(max_length=100, verbose_name="Статус поездки")

    class Meta:
        verbose_name = "Поездка Yandex"
        verbose_name_plural = "Поездки Yandex"

    def __str__(self):
        return f"Yandex Trip for Order {self.order.id}"