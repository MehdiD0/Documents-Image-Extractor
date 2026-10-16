
from pathlib import PurePosixPath
from zipfile import ZipFile


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
    ".emf",
    ".wmf",
    ".svg",
}


def extract_word_images(docx_path):
    """Return a list of (filename, image_bytes) pairs."""
    extracted_images = []

    with ZipFile(docx_path, "r") as docx:
        media_files = sorted(
            name
            for name in docx.namelist()
            if name.startswith("word/media/")
            and not name.endswith("/")
            and PurePosixPath(name).suffix.lower()
            in SUPPORTED_EXTENSIONS
        )

        for index, media_path in enumerate(media_files, start=1):
            filename = PurePosixPath(media_path).name
            image_bytes = docx.read(media_path)

            extracted_images.append(
                (filename, image_bytes)
            )

    return extracted_images
