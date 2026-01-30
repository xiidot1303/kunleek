from app.models import Product, Category, Shop, ProductByShop, FavoriteProduct
from config import BILLZ_SHOP_ID as shop_id, BILLZ_CATEGORY4_ID as category_custom_field_id
from decimal import Decimal
from django.db.models import OuterRef, Subquery, Exists, QuerySet


def create_product_from_billz(product_data):
    """Create or update Product objects (without shop-specific fields) and
    create/update ProductByShop entries for every shop provided in product_data.

    Returns list of billz_ids processed.
    """
    existing_products = Product.objects.in_bulk(field_name='billz_id')
    new_products = []
    products_to_update = []
    billz_ids = []
    existing_categories = Category.objects.in_bulk(field_name='name')

    # First pass: prepare Product instances (no shop-specific fields)
    for product in product_data:
        billz_id = product.get("id")
        name = product.get("name").split("/")[0].strip()
        description = ""
        sku = product.get("sku", "")
        main_photo = product.get("main_image_url_full")

        # get category name from custom fields (existing logic)
        category_name = None
        custom_fields = product.get("custom_fields", []) or []
        for custom_field in custom_fields:
            if custom_field.get("custom_field_id") == category_custom_field_id:
                category_name = str(custom_field.get("custom_field_value", "")).strip()

        photos = [photo.get('photo_url') for photo in product.get("photos", [])]

        category: Category = existing_categories.get(category_name, None)

        if billz_id in existing_products:
            product_obj = existing_products[billz_id]
            product_obj.name = name
            product_obj.category = category
            product_obj.description = description
            product_obj.photo = main_photo
            product_obj.photos = photos
            product_obj.sku = sku
            products_to_update.append(product_obj)
        else:
            product_obj = Product(
                billz_id=billz_id,
                name=name,
                category=category,
                description=description,
                photo=main_photo,
                photos=photos,
                sku=sku,
            )
            new_products.append(product_obj)

        billz_ids.append(billz_id)

    # bulk create or update products
    if new_products:
        Product.objects.bulk_create(new_products, batch_size=500)
    if products_to_update:
        Product.objects.bulk_update(
            products_to_update,
            ['name', 'category', 'description', 'photo', 'photos', 'sku'],
            batch_size=500
        )

    # Refresh products from DB to get PKs
    products = Product.objects.filter(billz_id__in=billz_ids)
    product_map = {p.billz_id: p for p in products}

    # Prepare shop and existing ProductByShop mappings
    existing_shops = Shop.objects.in_bulk(field_name='shop_id')
    existing_pbs_qs = ProductByShop.objects.filter(product__billz_id__in=billz_ids).select_related('shop', 'product')
    existing_pbs_map = {(pb.shop.shop_id, pb.product.billz_id): pb for pb in existing_pbs_qs}

    new_pbs = []
    pbs_to_update = []

    # Second pass: create/update ProductByShop per shop in incoming data
    for product in product_data:
        billz_id = product.get('id')
        product_obj = product_map.get(billz_id)
        if not product_obj:
            continue

        # For each shop price available for this product
        for shop_price in product.get('shop_prices', []):
            shop_billz_id = shop_price.get('shop_id')
            shop_obj = existing_shops.get(shop_billz_id)
            if not shop_obj:
                # skip shops not present in DB
                continue

            retail_price = shop_price.get('retail_price') or 0
            promo_price = shop_price.get('promo_price') or 0
            # prefer promo price if present
            price = Decimal(str(promo_price)) if promo_price else Decimal(str(retail_price))
            price_without_discount = Decimal(str(retail_price)) if retail_price else Decimal('0')

            # find quantity for this shop
            quantity = 0
            for sm in product.get('shop_measurement_values', []):
                if sm.get('shop_id') == shop_billz_id:
                    quantity = sm.get('active_measurement_value', 0) or 0
                    break

            key = (shop_billz_id, billz_id)
            existing_pb = existing_pbs_map.get(key)
            if existing_pb:
                existing_pb.price = price
                existing_pb.price_without_discount = price_without_discount
                existing_pb.quantity = quantity
                pbs_to_update.append(existing_pb)
            else:
                new_pb = ProductByShop(
                    shop=shop_obj,
                    product=product_obj,
                    price=price,
                    price_without_discount=price_without_discount,
                    quantity=quantity,
                )
                new_pbs.append(new_pb)

    # bulk create/update ProductByShop
    if new_pbs:
        ProductByShop.objects.bulk_create(new_pbs, batch_size=500)
    if pbs_to_update:
        ProductByShop.objects.bulk_update(pbs_to_update, ['price', 'price_without_discount', 'quantity'], batch_size=500)

    return billz_ids


def delete_products_not_in_billz(billz_ids):
    Product.objects.exclude(billz_id__in=billz_ids).delete()


def filter_products_for_serializer(
        queryset: QuerySet[Product], 
        user_id: int, 
        shop_id: int
        ) -> QuerySet[Product]:
    favorites = FavoriteProduct.objects.filter(user__user_id=user_id, product=OuterRef('pk'))
    products_by_shop = ProductByShop.objects.filter(shop_id=shop_id, product=OuterRef('pk'))
    products = queryset.filter(shops__shop_id=shop_id).annotate(
        is_favorite=Exists(favorites)).annotate(price=Subquery(products_by_shop.values('price')[:1]),
        price_without_discount=Subquery(products_by_shop.values('price_without_discount')[:1]),
        quantity=Subquery(products_by_shop.values('quantity')[:1]),
    ).order_by('price')
    return products