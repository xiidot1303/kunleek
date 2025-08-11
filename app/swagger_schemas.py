from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

toogle_favorite_product = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id', 'product_id'],
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product ID'),
            },
)

product_by_name = [
    openapi.Parameter(
        'name',
        openapi.IN_QUERY,
        description="Name of the product to search for",
        type=openapi.TYPE_STRING
    )
]