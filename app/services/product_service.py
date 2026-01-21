from app.models import Product, Category
from config import BILLZ_SHOP_ID as shop_id


def create_product_from_billz(product_data):
    existing_products = Product.objects.in_bulk(field_name='billz_id')
    new_products = []
    products_to_update = []
    billz_ids = []
    for product in product_data:
        billz_id = product.get("id")
        category_id = product['categories'][0]['id'] if product['categories'] else None
        name = product.get("name").split("/")[0].strip()
        # description = product.get("description", "")
        description = ""
        sku = product.get("sku", "")
        main_photo = product.get("main_image_url_full")
        # get quantity
        quantity = 0
        for shop_measurement in product.get("shop_measurement_values", []):
            if shop_measurement['shop_id'] == shop_id:
                quantity = shop_measurement['active_measurement_value']
                break
        # if not quantity:
        #     continue
        # get price
        price = 0
        discount_price = 0
        for shop_price in product.get("shop_prices", []):
            if shop_price['shop_id'] == shop_id:
                price = shop_price['retail_price']
                discount_price = shop_price['promo_price']
                break
        # if not price:
        #     continue
        
        # get category name
        category_name = None
        custom_fields = product.get("custom_fields", []) or []
        for custom_field in custom_fields:
            if custom_field["custom_field_id"] == "99440f1a-7030-4463-ad8e-71924388d4fe":
                category_name = str(custom_field["custom_field_value"]).strip()

        photos = [
            photo['photo_url']
            for photo in product.get("photos", [])
        ]
        # create or update product
        category: Category = Category.objects.filter(name=category_name).first() if category_name else None
        if billz_id in existing_products:
            product_obj = existing_products[billz_id]
            product_obj.name = name
            product_obj.category = category
            product_obj.description = description
            product_obj.price = discount_price or price
            product_obj.price_without_discount = price
            product_obj.photo = main_photo
            product_obj.photos = photos
            product_obj.sku = sku
            product_obj.quantity = quantity
            products_to_update.append(product_obj)
        else:
            product_obj = Product(
                billz_id=billz_id,
                name=name,
                category=category,
                description=description,
                price=discount_price or price,
                price_without_discount=price,
                photo=main_photo,
                photos=photos,
                sku=sku,
                quantity=quantity
            )
            new_products.append(product_obj)
        billz_ids.append(billz_id)

    # delete products which is not in Billz
    Product.objects.exclude(billz_id__in=billz_ids).delete()

    # bulk create or update products
    if new_products:
        Product.objects.bulk_create(new_products, batch_size=500)
    if products_to_update:
        Product.objects.bulk_update(
            products_to_update,
            ['name', 'category', 'description', 'price', 'price_without_discount', 'photo', 'photos', 'sku', 'quantity'],
            batch_size=500
        )