from config import BILLZ_SECRET_TOKEN
import requests
from django.core.cache import cache
from app.services.category_service import *
from app.services.product_service import *

def fetch_and_cache_access_token():
    url = "https://api-admin.billz.ai/v1/auth/login"
    payload = {"secret_token": BILLZ_SECRET_TOKEN}
    response = requests.post(url, json=payload)
    response_data = response.json()
    data = response_data.get("data", {})
    access_token = data.get("access_token")
    if access_token:
        cache.set("billz_access_token", access_token, timeout=86400)
    return access_token


def fetch_categories():
    url = "https://api-admin.billz.ai/v2/category"
    access_token = cache.get("billz_access_token") or fetch_and_cache_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response_data = response.json()
    categories = response_data.get("categories", [])
    
    create_category_from_billz(categories)


def fetch_products():
    url = "https://api-admin.billz.ai/v2/products"
    access_token = cache.get("billz_access_token") or fetch_and_cache_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    page = 1
    while True:
        params = {"page": page}
        response = requests.get(url, headers=headers, params=params)
        response_data = response.json()
        existing_products = Product.objects.in_bulk(field_name='billz_id')
        new_products = []
        products_to_update = []
        if products:=response_data.get("products", []):
            for product in products:
                billz_id = product.get("id")
                category_id = product['categories'][0]['id'] if product['categories'] else None
                name = product.get("name").split("/")[0].strip()
                description = product.get("description", "")
                sku = product.get("sku", "")
                main_photo = product.get("main_image_url_full")
                # get quantity
                quantity = None
                for shop_measurement in product.get("shop_measurement_values", []):
                    if shop_measurement['shop_id'] == "e1adc82b-5a22-4bbb-a1d5-0b3fe49f89da":
                        quantity = shop_measurement['active_measurement_value']
                        break
                if not quantity:
                    continue
                # get price
                price = None
                for shop_price in product.get("shop_prices", []):
                    if shop_price['shop_id'] == "e1adc82b-5a22-4bbb-a1d5-0b3fe49f89da":
                        price = shop_price['retail_price']
                        break
                if not price:
                    continue
                
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
        else:
            break
        
        page += 1
