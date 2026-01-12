from rest_framework import serializers
from app.models import *
from bot.models import Bot_user

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'name_uz', 'name_ru', 'photo', 'billz_id', 'subcategories'
        ]

    def get_subcategories(self, obj):
        # recursively serialize subcategories
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []

class DiscountCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCategory
        fields = ['id', 'name', 'index']


class ProductSerializer(serializers.ModelSerializer):
    is_favorite = serializers.BooleanField(read_only=True)
    discount_category = DiscountCategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'


class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = CustomerSerializer()
    bot_user = serializers.SlugRelatedField(
        slug_field='user_id',
        queryset=Bot_user.objects.all()
    )

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        # create new customer
        customer_data = validated_data.pop('customer')
        customer = Customer.objects.create(**customer_data)
        validated_data['customer'] = customer
        # create new order
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        return instance

class FavoriteProductSerializer(serializers.ModelSerializer):
    class ProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = '__all__'
            ref_name = 'FavoriteProduct_ProductSerializer'

    product = ProductSerializer(read_only=True)
    class Meta:
        model = FavoriteProduct
        fields = ['id', 'user', 'product']


class BotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot_user
        fields = '__all__'
        read_only_fields = ['date', 'user_id']