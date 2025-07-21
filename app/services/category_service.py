from app.models import Category


def create_category_from_billz(category_data, parent: Category=None):
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