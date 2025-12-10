from app.models import Product, Category
from config import BILLZ_SHOP_ID as shop_id


def create_product_from_billz(product_data):
    existing_products = Product.objects.in_bulk(field_name='billz_id')
    new_products = []
    products_to_update = []
    for product in product_data:
        billz_id = product.get("id")
        category_id = product['categories'][0]['id'] if product['categories'] else None
        name = product.get("name").split("/")[0].strip()
        description = product.get("description", "")
        sku = product.get("sku", "")
        main_photo = product.get("main_image_url_full")
        # get quantity
        quantity = None
        for shop_measurement in product.get("shop_measurement_values", []):
            if shop_measurement['shop_id'] == shop_id:
                quantity = shop_measurement['active_measurement_value']
                break
        # if not quantity:
        #     continue
        # get price
        price = None
        for shop_price in product.get("shop_prices", []):
            if shop_price['shop_id'] == shop_id:
                price = shop_price['retail_price']
                break
        # if not price:
        #     continue
        
        photos = [
            photo['photo_url']
            for photo in product.get("photos", [])
        ]
        # create or update product
        category: Category = Category.objects.filter(billz_id=category_id).first()
        if billz_id in existing_products:
            product_obj = existing_products[billz_id]
            product_obj.name = name
            product_obj.category = category
            product_obj.description = description
            product_obj.price = price
            product_obj.photo = main_photo
            product_obj.photos = photos
            product_obj.sku = sku,
            product_obj.quantity = quantity
            products_to_update.append(product_obj)
        else:
            product_obj = Product(
                billz_id=billz_id,
                name=name,
                category=category,
                description=description,
                price=price,
                photo=main_photo,
                photos=photos,
                sku=sku,
                quantity=quantity
            )
            new_products.append(product_obj)
    
    # bulk create or update products
    if new_products:
        Product.objects.bulk_create(new_products, batch_size=500)
    if products_to_update:
        Product.objects.bulk_update(
            products_to_update,
            ['name', 'category', 'description', 'price', 'photo', 'photos', 'sku', 'quantity'],
            batch_size=500
        )