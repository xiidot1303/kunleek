from django.db import models
    

class Category(models.Model):
    billz_id = models.CharField(max_length=128, null=True, blank=True, verbose_name="ID Billz")
    name = models.CharField(max_length=100, null=True, verbose_name="Название")
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


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    billz_id = models.CharField(max_length=128, unique=True, null=True, verbose_name="ID Billz")
    name = models.CharField(max_length=1024, verbose_name="Название")
    name_uz = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Название на узбекском")
    name_ru = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Название на русском")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    price_without_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена без скидки")
    photo = models.URLField(null=True, blank=True, verbose_name="URL фото")
    photos = models.JSONField(
        default=list,
        help_text="Список URL фото для продукта",
        verbose_name="Фото (список URL)"
    )
    sku = models.CharField(null=True, blank=True, max_length=100, verbose_name="Артикул (SKU)")
    quantity = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=0, verbose_name="Количество")
    mxik = models.CharField(max_length=100, null=True, blank=True, verbose_name="МХИК")
    package_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="Код упаковки")
    active = models.BooleanField(null=True, default=False)
    
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['name']
    

class FavoriteProduct(models.Model):
    user = models.ForeignKey('bot.Bot_user', on_delete=models.CASCADE, related_name='favorite_products', verbose_name="User")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites', verbose_name="Product")
    

class DeliveryType(models.Model):
    title_uz = models.CharField(max_length=255, null=True, verbose_name="Название (узбекский)")
    title_ru = models.CharField(max_length=255, null=True, verbose_name="Название (русский)")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Цена")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    TYPE_CHOICES = [
        ('express_yandex', 'Yandex'),
        ('during_day', 'В течение дня'),
    ]
    type = models.CharField(max_length=100, null=True, choices=TYPE_CHOICES, verbose_name="Тип")

    class Meta:
        verbose_name = "Тип доставки"
        verbose_name_plural = "Типы доставки"

    def __str__(self):
        return self.title_uz


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
    bot_user = models.ForeignKey('bot.Bot_user', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Пользователь бота")
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE, verbose_name="Клиент")
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name="Тип доставки")
    payment_method = models.CharField(max_length=50, verbose_name="Метод оплаты")
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
    status = models.CharField(max_length=50, null=True, blank=True, verbose_name="Статус")
    sent_to_group = models.BooleanField(default=False, verbose_name="Отправлено в группу")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order {self.id} by {self.customer.first_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    def __str__(self):
        return f"{self.product.name}"
    

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