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