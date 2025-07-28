from django.db import models
    

class Category(models.Model):
    billz_id = models.CharField(max_length=128, null=True, verbose_name="ID Billz")
    name = models.CharField(max_length=100, null=True, verbose_name="Name")
    name_uz = models.CharField(max_length=100, blank=True, null=True, verbose_name="Name in Uzbek")
    name_ru = models.CharField(max_length=100, blank=True, null=True, verbose_name="Name in Russian")
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    index = models.IntegerField(default=0, help_text="Order of the category in the list")

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Category"
    )
    billz_id = models.CharField(max_length=128, unique=True, null=True, verbose_name="ID Billz")
    name = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100, blank=True, null=True)
    name_ru = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.URLField(null=True, blank=True, verbose_name="Photo URL")
    photos = models.JSONField(
        default=list,
        help_text="List of photo URLs for the product"
    )
    sku = models.CharField(null=True, blank=True, max_length=100, verbose_name="SKU")
    quantity = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=0, verbose_name="Quantity")
    
    
    def __str__(self):
        return self.name
    


class DeliveryType(models.Model):
    title_uz = models.CharField(max_length=255, null=True, verbose_name="Название (узбекский)")
    title_ru = models.CharField(max_length=255, null=True, verbose_name="Название (русский)")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Цена")

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
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая сумма")
    notes = models.TextField(blank=True, null=True, verbose_name="Заметки")
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