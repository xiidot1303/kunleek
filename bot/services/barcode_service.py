from barcode import EAN13
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile


async def generate_barcode(user_id: int, barcode: str) -> str:
    """
    Generate a barcode image for the given user ID and barcode string.
    """

    # Create a barcode object
    ean = EAN13(barcode, writer=ImageWriter())

    # Generate the barcode image
    buffer = BytesIO()
    ean.write(buffer)

    # Save the image to a Django FileField
    file_name = f"barcode_{user_id}.png"
    content_file = ContentFile(buffer.getvalue(), name=file_name)

    return content_file.name, content_file