try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


def ocr_core(filename):
    tessdata_dir_config = "/usr/share/tesseract-ocr/4.00/tessdata"
    """
    This function will handle the core OCR processing of images.
    """
    text = pytesseract.image_to_string(Image.open(filename), lang="amh",config=tessdata_dir_config)  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text  # Then we will print the text in the image
