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

product_by_name_param = openapi.Parameter(
    'name',
    openapi.IN_QUERY,
    description="Name of the product to search for",
    type=openapi.TYPE_STRING
)

# common shop_id query parameter used across product endpoints
shop_id_param = openapi.Parameter(
    'shop_id',
    openapi.IN_QUERY,
    description='Shop ID',
    type=openapi.TYPE_INTEGER
)

user_id_param = openapi.Parameter(
    'user_id',
    openapi.IN_QUERY,
    description='User ID',
    type=openapi.TYPE_STRING,
    required=False
)
