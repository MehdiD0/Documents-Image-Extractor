import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pymupdf
from PySide6.QtWidgets import QApplication

from main import MainWindow, open_folder_in_explorer

def test_preview_and_window():
    # Use offscreen platform for headless test
    app = QApplication.instance()
    if not app:
        app = QApplication(["", "-platform", "offscreen"])

    window = MainWindow()

    # Create dummy PDF
    test_pdf_path = Path("test_sample.pdf")
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Sample Doc for Preview")
    doc.save(str(test_pdf_path))
    doc.close()

    try:
        # Test adding document
        window.add_documents([str(test_pdf_path.resolve())])
        assert len(window.documents) == 1
        assert window.file_list.count() == 1

        # Test selecting document and preview
        window.on_document_selected(0)
        assert window.current_doc_path == test_pdf_path.resolve()
        assert window.current_preview_total == 1
        assert window.preview_stack.currentIndex() == 1
        assert window.preview_image_label._pixmap is not None
        assert not window.preview_image_label._pixmap.isNull()
        print("PDF Preview loaded successfully! Pixmap valid:", not window.preview_image_label._pixmap.isNull())

        # Test clear
        window.clear_documents()
        assert len(window.documents) == 0
        assert window.file_list.count() == 0
        assert window.preview_stack.currentIndex() == 0
        print("Clear documents passed!")

    finally:
        if test_pdf_path.exists():
            test_pdf_path.unlink()

    # Test DOCX with image
    import zipfile
    test_docx_path = Path("test_sample.docx")
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage, QColor
    test_img = QImage(10, 10, QImage.Format.Format_RGB32)
    test_img.fill(QColor("red"))
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    test_img.save(buf, "PNG")
    dummy_png = bytes(buf.data())
    with zipfile.ZipFile(test_docx_path, "w") as z:
        z.writestr("word/media/image1.png", dummy_png)
        z.writestr("word/document.xml", "<w:document><w:body><w:p><w:r><w:t>Sample Word text</w:t></w:r></w:p></w:body></w:document>")

    try:
        window.add_documents([str(test_docx_path.resolve())])
        assert len(window.documents) == 1
        window.on_document_selected(0)
        assert window.current_preview_total == 1
        assert window.preview_stack.currentIndex() == 1
        assert window.preview_image_label._pixmap is not None
        assert not window.preview_image_label._pixmap.isNull()
        print("DOCX Image Preview loaded successfully!")
    finally:
        if test_docx_path.exists():
            test_docx_path.unlink()

if __name__ == "__main__":
    import os
    test_preview_and_window()
    print("ALL TESTS PASSED!")
    os._exit(0)
