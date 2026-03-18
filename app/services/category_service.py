from app.models import Category, Product
from django.db.models import Count, Q


def create_category_from_billz(category_data, parent: Category = None):
    """
    Create or update a category from Billz data.
    """
    for category in category_data:
        category_id = category.get("id")
        category_obj, created = Category.objects.get_or_create(
            billz_id=category_id,
            defaults={
                'name': category.get("name"),
                'parent_category': parent,
            }
        )
        if not created:
            category_obj.name = category.get("name")
            category_obj.parent_category = parent
            category_obj.save()

        subRows = category.get("subRows", [])
        if subRows:
            create_category_from_billz(subRows, parent=category_obj)


def get_descendant_ids(category):
    """Recursively collect all descendant IDs of a category"""
    ids = []
    for child in category.subcategories.all():
        ids.append(child.id)
        ids.extend(get_descendant_ids(child))
    return ids


def list_categories_id_in_sell() -> list:
    """List of categories ID"""
    main_categories = []

    for cat in Category.objects.filter(parent_category__isnull=True):
        descendant_ids = get_descendant_ids(cat)
        has_products = Product.objects.filter(
            category_id__in=descendant_ids, quantity__gt=0).exists()
        if has_products:
            main_categories.append(cat.id)

    return main_categories


def create_category_by_data(category_data, parent: Category = None):
    for category, subcategories in category_data.items():
        category_obj, created = Category.objects.get_or_create(
            name=category,
            defaults={
                'parent_category': parent,
                'name_ru': category
            }
        )
        if subcategories:
            create_category_by_data(subcategories, parent=category_obj)


def deactivate_categories_if_empty():
    """
    Deactivate categories that have no active products
    and parent categories that have no active subcategories. 
    """
    # Mark all categories active first
    Category.objects.all().update(active=True)

    # Assumption: a product is "active" when `quantity > 0`.
    # 1) Deactivate leaf categories (no subcategories) that have no active products.
    leaf_qs = Category.objects.annotate(
        child_count=Count('subcategories'),
        active_product_count=Count('products', filter=Q(products__active=True)),
    ).filter(child_count=0, active_product_count=0)

    leaf_ids = list(leaf_qs.values_list('id', flat=True))
    if leaf_ids:
        Category.objects.filter(id__in=leaf_ids).update(active=False)

    # 2) Iteratively deactivate parent categories that have no active subcategories.
    # Use set-based queries to find all parents with zero active children and deactivate in bulk.
    while True:
        parents_to_deactivate = Category.objects.annotate(
            active_subcats=Count('subcategories', filter=Q(subcategories__active=True)),
        ).filter(active_subcats=0, subcategories__isnull=False, active=True)

        parent_ids = list(parents_to_deactivate.values_list('id', flat=True))
        if not parent_ids:
            break

        Category.objects.filter(id__in=parent_ids).update(active=False)