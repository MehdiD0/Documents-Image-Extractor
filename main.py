import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

import pymupdf
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QIcon, QImage, QPixmap

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "assets" / "icon.png"
ICO_PATH = BASE_DIR / "assets" / "icon.ico"


def get_app_icon() -> QIcon:
    """Return a multi-resolution QIcon for taskbar and title bar."""
    icon = QIcon()
    if ICO_PATH.exists():
        icon = QIcon(str(ICO_PATH))
    elif ICON_PATH.exists():
        icon = QIcon(str(ICON_PATH))

    if ICON_PATH.exists():
        base_pix = QPixmap(str(ICON_PATH))
        if not base_pix.isNull():
            for size in (16, 20, 24, 32, 48, 64, 128, 256):
                icon.addPixmap(
                    base_pix.scaled(
                        size,
                        size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
    return icon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from extractors.pdf_extractor import extract_pdf_images
from extractors.word_extractor import SUPPORTED_EXTENSIONS, extract_word_images


DARK_STYLE = """
QMainWindow, QWidget#centralWidget {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: "Segoe UI", -apple-system, sans-serif;
    font-size: 10pt;
}

QWidget {
    color: #F8FAFC;
    font-family: "Segoe UI", -apple-system, sans-serif;
    font-size: 10pt;
}

QLabel {
    background: transparent;
    background-color: transparent;
}

QStackedWidget, QStackedWidget > QWidget {
    background: transparent;
    background-color: transparent;
    border: none;
}

QLabel#title {
    font-size: 22pt;
    font-weight: 700;
    color: #F8FAFC;
    background: transparent;
}

QLabel#subtitle {
    color: #94A3B8;
    font-size: 10pt;
    background: transparent;
}

QLabel#sectionHeader {
    font-weight: 600;
    font-size: 11pt;
    color: #E2E8F0;
    background: transparent;
}

QLabel#navLabel {
    color: #CBD5E1;
    font-size: 9pt;
    font-weight: 600;
    padding: 0 4px;
    background: transparent;
}

QLabel#emptyText {
    color: #94A3B8;
    font-size: 11pt;
    font-weight: 500;
    background: transparent;
}

QLabel#dropLabel {
    font-size: 13pt;
    font-weight: 600;
    color: #F8FAFC;
    border: none;
    background: transparent;
}

QLabel#outputLabel {
    color: #CBD5E1;
    font-size: 9.5pt;
    background: transparent;
}

QLabel#previewInfo {
    font-size: 9pt;
    color: #94A3B8;
    background: transparent;
}

QFrame#dropZone {
    background-color: #1E293B;
    border: 2px dashed #475569;
    border-radius: 12px;
}

QFrame#dropZone:hover {
    border-color: #38BDF8;
    background-color: #1A2E46;
}

QFrame#sectionBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
}

QListWidget {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
    margin-bottom: 2px;
    color: #F1F5F9;
}

QListWidget::item:hover {
    background-color: #334155;
}

QListWidget::item:selected {
    background-color: #1E3A8A;
    color: #93C5FD;
    font-weight: 600;
}

QPushButton {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 1px solid #475569;
    border-radius: 7px;
    padding: 8px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #64748B;
}

QPushButton:disabled {
    color: #64748B;
    background-color: #0F172A;
    border-color: #334155;
}

QPushButton#primary {
    background-color: #2563EB;
    color: white;
    font-weight: 600;
    border: none;
    padding: 9px 18px;
}

QPushButton#primary:hover {
    background-color: #1D4ED8;
}

QPushButton#danger {
    background-color: #3B1219;
    color: #FCA5A5;
    border: 1px solid #EF4444;
    border-radius: 6px;
    padding: 3px 12px;
    font-size: 9pt;
    font-weight: 600;
}

QPushButton#danger:hover {
    background-color: #DC2626;
    color: #FFFFFF;
    border-color: #EF4444;
}

QPushButton#navBtn {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 0px;
    font-size: 11pt;
    font-weight: 700;
}

QPushButton#navBtn:hover {
    background-color: #334155;
    border-color: #38BDF8;
    color: #38BDF8;
}

QPushButton#navBtn:pressed {
    background-color: #1E3A8A;
}

QPushButton#navBtn:disabled {
    background-color: #0F172A;
    border-color: #334155;
    color: #475569;
}

QPushButton#themeToggle {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 1px solid #475569;
    border-radius: 18px;
    padding: 5px 14px;
    font-size: 9.5pt;
    font-weight: 600;
}

QPushButton#themeToggle:hover {
    background-color: #334155;
    border-color: #F59E0B;
    color: #FBBF24;
}

QTextEdit#previewTextEdit {
    background-color: #0F172A;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 10px;
}

QSplitter::handle {
    background-color: #0F172A;
}
"""

LIGHT_STYLE = """
QMainWindow, QWidget#centralWidget {
    background-color: #F8FAFD;
    color: #1E293B;
    font-family: "Segoe UI", -apple-system, sans-serif;
    font-size: 10pt;
}

QWidget {
    color: #1E293B;
    font-family: "Segoe UI", -apple-system, sans-serif;
    font-size: 10pt;
}

QLabel {
    background: transparent;
    background-color: transparent;
}

QStackedWidget, QStackedWidget > QWidget {
    background: transparent;
    background-color: transparent;
    border: none;
}

QLabel#title {
    font-size: 22pt;
    font-weight: 700;
    color: #0F172A;
    background: transparent;
}

QLabel#subtitle {
    color: #64748B;
    font-size: 10pt;
    background: transparent;
}

QLabel#sectionHeader {
    font-weight: 600;
    font-size: 11pt;
    color: #1E293B;
    background: transparent;
}

QLabel#navLabel {
    color: #475569;
    font-size: 9pt;
    font-weight: 600;
    padding: 0 4px;
    background: transparent;
}

QLabel#emptyText {
    color: #94A3B8;
    font-size: 11pt;
    font-weight: 500;
    background: transparent;
}

QLabel#dropLabel {
    font-size: 13pt;
    font-weight: 600;
    color: #1E293B;
    border: none;
    background: transparent;
}

QLabel#outputLabel {
    color: #334155;
    font-size: 9.5pt;
    background: transparent;
}

QLabel#previewInfo {
    font-size: 9pt;
    color: #64748B;
    background: transparent;
}

QFrame#dropZone {
    background-color: #FFFFFF;
    border: 2px dashed #CBD5E1;
    border-radius: 12px;
}

QFrame#dropZone:hover {
    border-color: #3B82F6;
    background-color: #F0F7FF;
}

QFrame#sectionBox {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
}

QListWidget {
    background-color: #FFFFFF;
    color: #1E293B;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
    margin-bottom: 2px;
    color: #1E293B;
}

QListWidget::item:hover {
    background-color: #F1F5F9;
}

QListWidget::item:selected {
    background-color: #EFF6FF;
    color: #1D4ED8;
    font-weight: 600;
}

QPushButton {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
    padding: 8px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #F1F5F9;
    border-color: #94A3B8;
}

QPushButton:disabled {
    color: #94A3B8;
    background-color: #F8FAFC;
    border-color: #E2E8F0;
}

QPushButton#primary {
    background-color: #2563EB;
    color: white;
    font-weight: 600;
    border: none;
    padding: 9px 18px;
}

QPushButton#primary:hover {
    background-color: #1D4ED8;
}

QPushButton#danger {
    background-color: #FEE2E2;
    color: #B91C1C;
    border: 1px solid #F87171;
    border-radius: 6px;
    padding: 3px 12px;
    font-size: 9pt;
    font-weight: 600;
}

QPushButton#danger:hover {
    background-color: #EF4444;
    color: #FFFFFF;
    border-color: #EF4444;
}

QPushButton#navBtn {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 0px;
    font-size: 11pt;
    font-weight: 700;
}

QPushButton#navBtn:hover {
    background-color: #EFF6FF;
    border-color: #3B82F6;
    color: #1D4ED8;
}

QPushButton#navBtn:pressed {
    background-color: #DBEAFE;
}

QPushButton#navBtn:disabled {
    background-color: #F8FAFC;
    border-color: #E2E8F0;
    color: #94A3B8;
}

QPushButton#themeToggle {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 18px;
    padding: 5px 14px;
    font-size: 9.5pt;
    font-weight: 600;
}

QPushButton#themeToggle:hover {
    background-color: #F1F5F9;
    border-color: #6366F1;
    color: #4F46E5;
}

QTextEdit#previewTextEdit {
    background-color: #F8FAFC;
    color: #334155;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 10px;
}

QSplitter::handle {
    background-color: #F8FAFD;
}
"""

APP_STYLE = DARK_STYLE


def safe_folder_name(name: str) -> str:
    """Remove characters forbidden in Windows folder names."""
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", name)
    return cleaned.strip(" .") or "document"


def open_folder_in_explorer(folder_path: Path):
    """Open a directory in the native file manager."""
    try:
        resolved = folder_path.resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(resolved))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(resolved)])
        else:
            subprocess.Popen(["xdg-open", str(resolved)])
    except Exception:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))


def format_file_size(num_bytes: int) -> str:
    """Return human readable file size string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}" if unit != "B" else f"{num_bytes} B"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"


class ImagePreviewLabel(QLabel):
    """Scalable image preview widget that maintains aspect ratio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )

    def set_pixmap(self, pixmap: QPixmap | None):
        self._pixmap = pixmap
        self.update_display()

    def update_display(self):
        if self._pixmap and not self._pixmap.isNull():
            w = max(10, self.width() - 8)
            h = max(10, self.height() - 8)
            scaled = self._pixmap.scaled(
                w,
                h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            super().setPixmap(scaled)
        else:
            super().setPixmap(QPixmap())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Documents Image-Extractor")
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self.resize(960, 680)
        self.setAcceptDrops(True)

        self.documents: list[Path] = []
        self.output_dir = Path.home() / "Pictures" / "ExtractedImages"

        # Preview state for currently selected document
        self.current_doc_path: Path | None = None
        self.current_preview_index = 0
        self.current_preview_total = 0
        self.docx_images_cache: list[tuple[str, bytes]] = []

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(28, 20, 28, 20)
        main_layout.setSpacing(14)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        if ICON_PATH.exists():
            app_icon_label = QLabel()
            app_pix = QPixmap(str(ICON_PATH)).scaled(
                32,
                32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            app_icon_label.setPixmap(app_pix)
            title_row.addWidget(app_icon_label)

        title = QLabel("Documents Image-Extractor")
        title.setObjectName("title")
        title_row.addWidget(title)
        title_row.addStretch()

        self.theme_toggle_btn = QPushButton("☀️ Light")
        self.theme_toggle_btn.setObjectName("themeToggle")
        self.theme_toggle_btn.setToolTip("Switch between Dark and Light mode")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        title_row.addWidget(self.theme_toggle_btn)

        subtitle = QLabel("Extract images from PDF and Word documents.")
        subtitle.setObjectName("subtitle")

        header_layout.addLayout(title_row)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # 1st Box: Drop Zone
        self.drop_zone = QFrame()
        self.drop_zone.setObjectName("dropZone")
        self.drop_zone.setMinimumHeight(105)

        drop_layout = QVBoxLayout(self.drop_zone)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.setSpacing(6)

        drop_label = QLabel("📥  Drop PDF or DOCX files here")
        drop_label.setObjectName("dropLabel")
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        browse_button = QPushButton("Browse documents")
        browse_button.clicked.connect(self.browse_files)

        drop_layout.addWidget(drop_label)
        drop_layout.addWidget(browse_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.drop_zone)

        # 2nd Area: Splitter containing Document List & Document Preview Box
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)

        # Left Column: Selected Documents List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)

        list_header_layout = QHBoxLayout()
        self.list_header_label = QLabel("Selected documents (0)")
        self.list_header_label.setObjectName("sectionHeader")
        list_header_layout.addWidget(self.list_header_label)
        list_header_layout.addStretch()

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("danger")
        self.clear_btn.setFixedHeight(28)
        self.clear_btn.clicked.connect(self.clear_documents)
        list_header_layout.addWidget(self.clear_btn)
        left_layout.addLayout(list_header_layout)

        self.file_list = QListWidget()
        self.file_list.currentRowChanged.connect(self.on_document_selected)
        left_layout.addWidget(self.file_list, 1)

        # Right Column: 2nd Box (Preview Box)
        right_widget = QFrame()
        right_widget.setObjectName("sectionBox")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(14, 12, 14, 12)
        right_layout.setSpacing(10)

        # Preview Header bar
        preview_header = QHBoxLayout()
        self.preview_title_label = QLabel("Document Preview")
        self.preview_title_label.setObjectName("sectionHeader")
        preview_header.addWidget(self.preview_title_label)

        preview_header.addStretch()

        # Page / Image Navigation Buttons
        self.nav_prev_btn = QPushButton("◀")
        self.nav_prev_btn.setObjectName("navBtn")
        self.nav_prev_btn.setFixedSize(32, 28)
        self.nav_prev_btn.setToolTip("Previous page / image")
        self.nav_prev_btn.clicked.connect(self.preview_prev)
        self.nav_prev_btn.setEnabled(False)

        self.nav_label = QLabel("—")
        self.nav_label.setObjectName("navLabel")

        self.nav_next_btn = QPushButton("▶")
        self.nav_next_btn.setObjectName("navBtn")
        self.nav_next_btn.setFixedSize(32, 28)
        self.nav_next_btn.setToolTip("Next page / image")
        self.nav_next_btn.clicked.connect(self.preview_next)
        self.nav_next_btn.setEnabled(False)

        preview_header.addWidget(self.nav_prev_btn)
        preview_header.addWidget(self.nav_label)
        preview_header.addWidget(self.nav_next_btn)
        right_layout.addLayout(preview_header)

        # Preview Container / Stacked Pages
        self.preview_stack = QStackedWidget()
        self.preview_stack.setFrameShape(QFrame.Shape.NoFrame)

        # Page 0: Empty state placeholder
        self.empty_page = QWidget()
        empty_layout = QVBoxLayout(self.empty_page)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon = QLabel("📄")
        empty_icon.setStyleSheet("font-size: 38pt;")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text = QLabel("Select a document to preview")
        empty_text.setObjectName("emptyText")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_text)
        self.preview_stack.addWidget(self.empty_page)

        # Page 1: Image Viewport (for PDF pages and DOCX extracted images)
        self.image_page = QWidget()
        image_layout = QVBoxLayout(self.image_page)
        image_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_image_label = ImagePreviewLabel()
        image_layout.addWidget(self.preview_image_label)
        self.preview_stack.addWidget(self.image_page)

        # Page 2: Text / Info Fallback (for DOCX with no embedded images)
        self.text_page = QWidget()
        text_layout = QVBoxLayout(self.text_page)
        text_layout.setContentsMargins(8, 8, 8, 8)
        self.docx_info_banner = QLabel("Word Document Overview")
        self.docx_info_banner.setObjectName("sectionHeader")
        self.docx_text_preview = QTextEdit()
        self.docx_text_preview.setObjectName("previewTextEdit")
        self.docx_text_preview.setReadOnly(True)
        text_layout.addWidget(self.docx_info_banner)
        text_layout.addWidget(self.docx_text_preview, 1)
        self.preview_stack.addWidget(self.text_page)

        right_layout.addWidget(self.preview_stack, 1)

        # Preview Footer Info Label
        self.preview_info_label = QLabel("No document selected")
        self.preview_info_label.setObjectName("previewInfo")
        right_layout.addWidget(self.preview_info_label)

        content_splitter.addWidget(left_widget)
        content_splitter.addWidget(right_widget)
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 5)

        main_layout.addWidget(content_splitter, 1)

        # Output folder row
        output_row = QHBoxLayout()
        self.output_label = QLabel()
        self.output_label.setObjectName("outputLabel")
        self.update_output_label()
        output_row.addWidget(self.output_label, 1)

        output_button = QPushButton("Choose folder")
        output_button.clicked.connect(self.choose_output_folder)
        output_row.addWidget(output_button)

        open_folder_button = QPushButton("Open folder")
        open_folder_button.clicked.connect(lambda: open_folder_in_explorer(self.output_dir))
        output_row.addWidget(open_folder_button)

        extract_button = QPushButton("Extract images")
        extract_button.setObjectName("primary")
        extract_button.clicked.connect(self.extract_images)
        output_row.addWidget(extract_button)

        main_layout.addLayout(output_row)

        # Status Bar
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("subtitle")
        main_layout.addWidget(self.status_label)

        # Apply default theme (Dark mode)
        self.is_dark_mode = True
        self.apply_theme()

    def apply_theme(self):
        """Apply active theme stylesheet and update switcher state."""
        if self.is_dark_mode:
            self.setStyleSheet(DARK_STYLE)
            self.theme_toggle_btn.setText("☀️ Light")
            self.theme_toggle_btn.setToolTip("Switch to Light mode")
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self.theme_toggle_btn.setText("🌙 Dark")
            self.theme_toggle_btn.setToolTip("Switch to Dark mode")

    def toggle_theme(self):
        """Toggle between Dark and Light mode."""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def browse_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select documents",
            str(Path.home()),
            "Documents (*.pdf *.docx)",
        )
        self.add_documents(paths)

    def add_documents(self, paths):
        initial_count = len(self.documents)
        for path in paths:
            p = Path(path)
            if not p.is_file():
                continue
            if p.suffix.lower() not in {".pdf", ".docx"}:
                continue
            if p not in self.documents:
                self.documents.append(p)
                icon = "📕" if p.suffix.lower() == ".pdf" else "📘"
                item = QListWidgetItem(f"{icon}  {p.name}")
                item.setToolTip(str(p))
                self.file_list.addItem(item)

        self.list_header_label.setText(f"Selected documents ({len(self.documents)})")
        self.status_label.setText(f"{len(self.documents)} document(s) selected")

        # Automatically select the first or newly added document if not selected
        if len(self.documents) > 0 and self.file_list.currentRow() < 0:
            self.file_list.setCurrentRow(0)
        elif len(self.documents) > initial_count and initial_count == 0:
            self.file_list.setCurrentRow(0)

    def clear_documents(self):
        self.documents.clear()
        self.file_list.clear()
        self.list_header_label.setText("Selected documents (0)")
        self.status_label.setText("Ready")
        self.clear_preview()

    def on_document_selected(self, row: int):
        if row < 0 or row >= len(self.documents):
            self.clear_preview()
            return
        doc_path = self.documents[row]
        self.load_document_preview(doc_path)

    def clear_preview(self):
        self.current_doc_path = None
        self.current_preview_index = 0
        self.current_preview_total = 0
        self.docx_images_cache = []
        self.preview_title_label.setText("Document Preview")
        self.nav_label.setText("—")
        self.nav_prev_btn.setEnabled(False)
        self.nav_next_btn.setEnabled(False)
        self.preview_image_label.set_pixmap(None)
        self.preview_info_label.setText("No document selected")
        self.preview_stack.setCurrentIndex(0)

    def load_document_preview(self, path: Path):
        self.current_doc_path = path
        self.current_preview_index = 0
        self.docx_images_cache = []

        file_size_str = format_file_size(path.stat().st_size)

        if path.suffix.lower() == ".pdf":
            try:
                with pymupdf.open(path) as pdf:
                    self.current_preview_total = len(pdf)

                self.preview_title_label.setText(f"Preview: {path.name}")
                self.render_pdf_current_page()
                self.preview_info_label.setText(
                    f"PDF Document • {self.current_preview_total} page(s) • Size: {file_size_str}"
                )
            except Exception as e:
                self.preview_stack.setCurrentIndex(2)
                self.docx_info_banner.setText("Could not load PDF preview")
                self.docx_text_preview.setPlainText(str(e))
                self.preview_info_label.setText(f"Error loading PDF: {path.name}")

        elif path.suffix.lower() == ".docx":
            try:
                images, text_excerpt = self.get_docx_info(path)
                self.docx_images_cache = images
                self.current_preview_total = len(images)
                self.preview_title_label.setText(f"Preview: {path.name}")

                if self.current_preview_total > 0:
                    self.render_docx_current_image()
                    self.preview_info_label.setText(
                        f"Word Document • {self.current_preview_total} image(s) found • Size: {file_size_str}"
                    )
                else:
                    self.preview_stack.setCurrentIndex(2)
                    self.docx_info_banner.setText(
                        f"Word Document • No embedded images found • Size: {file_size_str}"
                    )
                    snippet = text_excerpt if text_excerpt else "(No readable text paragraphs found)"
                    self.docx_text_preview.setPlainText(
                        f"Document: {path.name}\n\nContent excerpt:\n{snippet}"
                    )
                    self.nav_label.setText("No images")
                    self.nav_prev_btn.setEnabled(False)
                    self.nav_next_btn.setEnabled(False)
                    self.preview_info_label.setText(
                        f"Word Document • Size: {file_size_str} • 0 images to extract"
                    )
            except Exception as e:
                self.preview_stack.setCurrentIndex(2)
                self.docx_info_banner.setText("Could not load DOCX preview")
                self.docx_text_preview.setPlainText(str(e))
                self.preview_info_label.setText(f"Error loading DOCX: {path.name}")

    def render_pdf_current_page(self):
        if not self.current_doc_path or self.current_preview_total == 0:
            return

        try:
            with pymupdf.open(self.current_doc_path) as pdf:
                page = pdf.load_page(self.current_preview_index)
                pix = page.get_pixmap(dpi=140)
                fmt = (
                    QImage.Format.Format_RGBA8888
                    if pix.alpha
                    else QImage.Format.Format_RGB888
                )
                img = QImage(
                    pix.samples,
                    pix.width,
                    pix.height,
                    pix.stride,
                    fmt,
                )
                pixmap = QPixmap.fromImage(img.copy())

            self.preview_image_label.set_pixmap(pixmap)
            self.preview_stack.setCurrentIndex(1)

            # Update pagination controls
            curr = self.current_preview_index + 1
            tot = self.current_preview_total
            self.nav_label.setText(f"Page {curr} of {tot}")
            self.nav_prev_btn.setEnabled(self.current_preview_index > 0)
            self.nav_next_btn.setEnabled(self.current_preview_index < tot - 1)
        except Exception as e:
            self.preview_info_label.setText(f"Failed to render page: {e}")

    def render_docx_current_image(self):
        if not self.docx_images_cache or self.current_preview_total == 0:
            return

        img_name, img_bytes = self.docx_images_cache[self.current_preview_index]
        qimg = QImage.fromData(img_bytes)

        if not qimg.isNull():
            pixmap = QPixmap.fromImage(qimg)
            self.preview_image_label.set_pixmap(pixmap)
            self.preview_stack.setCurrentIndex(1)
        else:
            # Fallback if image format not decoded by QImage
            self.preview_stack.setCurrentIndex(2)
            self.docx_info_banner.setText(f"Image: {img_name}")
            self.docx_text_preview.setPlainText(
                f"Binary image data: {len(img_bytes)} bytes.\nFile: {img_name}\nFormat not directly previewable in viewer, but extractable."
            )

        curr = self.current_preview_index + 1
        tot = self.current_preview_total
        self.nav_label.setText(f"Image {curr} of {tot}")
        self.nav_prev_btn.setEnabled(self.current_preview_index > 0)
        self.nav_next_btn.setEnabled(self.current_preview_index < tot - 1)

    def preview_prev(self):
        if self.current_preview_index > 0:
            self.current_preview_index -= 1
            if self.current_doc_path and self.current_doc_path.suffix.lower() == ".pdf":
                self.render_pdf_current_page()
            else:
                self.render_docx_current_image()

    def preview_next(self):
        if self.current_preview_index < self.current_preview_total - 1:
            self.current_preview_index += 1
            if self.current_doc_path and self.current_doc_path.suffix.lower() == ".pdf":
                self.render_pdf_current_page()
            else:
                self.render_docx_current_image()

    def get_docx_info(self, docx_path: Path) -> tuple[list[tuple[str, bytes]], str]:
        """Extract images and text excerpt from DOCX."""
        images = []
        text_preview = ""
        with ZipFile(docx_path, "r") as docx:
            # Images
            media_files = sorted(
                name
                for name in docx.namelist()
                if name.startswith("word/media/")
                and not name.endswith("/")
                and PurePosixPath(name).suffix.lower() in SUPPORTED_EXTENSIONS
            )
            for m in media_files:
                images.append((PurePosixPath(m).name, docx.read(m)))

            # Text
            if "word/document.xml" in docx.namelist():
                try:
                    xml_content = docx.read("word/document.xml")
                    root = ET.fromstring(xml_content)
                    texts = [
                        elem.text
                        for elem in root.iter()
                        if elem.tag.endswith("}t") and elem.text
                    ]
                    text_preview = " ".join(texts)[:600]
                except Exception:
                    text_preview = ""

        return images, text_preview

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile()
        ]
        self.add_documents(paths)
        event.acceptProposedAction()

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose output folder",
            str(self.output_dir),
        )
        if folder:
            self.output_dir = Path(folder)
            self.update_output_label()

    def update_output_label(self):
        self.output_label.setText(f"📁 Output folder: {self.output_dir}")

    def extract_images(self):
        if not self.documents:
            QMessageBox.warning(
                self,
                "No documents",
                "Please select at least one PDF or DOCX file.",
            )
            return

        total_images = 0
        failures = []
        self.output_dir.mkdir(parents=True, exist_ok=True)
        created_destinations = []

        for document in self.documents:
            try:
                if document.suffix.lower() == ".pdf":
                    images = extract_pdf_images(document)
                else:
                    images = extract_word_images(document)

                destination = self.output_dir / safe_folder_name(document.stem)
                destination.mkdir(parents=True, exist_ok=True)
                created_destinations.append(destination)

                saved = 0
                for filename, image_bytes in images:
                    target = destination / filename

                    # Avoid overwriting an existing file.
                    counter = 1
                    while target.exists():
                        target = destination / (
                            f"{Path(filename).stem}_{counter}"
                            f"{Path(filename).suffix}"
                        )
                        counter += 1

                    target.write_bytes(image_bytes)
                    saved += 1

                total_images += saved

            except Exception as error:
                failures.append(f"{document.name}: {error}")

        message = f"Extracted {total_images} image(s)."
        if failures:
            message += (
                "\n\nSome documents could not be processed:\n"
                + "\n".join(failures)
            )

        self.status_label.setText(
            f"Finished: {total_images} image(s) extracted"
        )

        # Automatically open the folder where the user chose to put the extracted images
        folder_to_open = (
            created_destinations[0]
            if len(created_destinations) == 1 and created_destinations[0].exists()
            else self.output_dir
        )
        open_folder_in_explorer(folder_to_open)

        QMessageBox.information(self, "Extraction complete", message)


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "documents.image.extractor.app"
            )
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    window = MainWindow()
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
    window.show()

    sys.exit(app.exec())
