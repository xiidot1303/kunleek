from app.models import Category, Product


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
            main_categories.append(cat)

    return main_categories
