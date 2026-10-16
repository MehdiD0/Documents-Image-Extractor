import pymupdf


def extract_pdf_images(pdf_path):
    """Return a list of (filename, image_bytes) pairs."""
    extracted_images = []
    seen_xrefs = set()

    with pymupdf.open(pdf_path) as pdf:
        for page in pdf:
            for image_info in page.get_images(full=True):
                xref = image_info[0]

                if xref in seen_xrefs:
                    continue

                seen_xrefs.add(xref)

                try:
                    image = pdf.extract_image(xref)

                    if not image or not image.get("image"):
                        continue

                    extension = image.get("ext", "bin")
                    filename = (
                        f"image_{len(extracted_images) + 1:03d}."
                        f"{extension}"
                    )

                    extracted_images.append(
                        (filename, image["image"])
                    )

                except Exception as error:
                    print(f"Could not extract image {xref}: {error}")

    return extracted_images
