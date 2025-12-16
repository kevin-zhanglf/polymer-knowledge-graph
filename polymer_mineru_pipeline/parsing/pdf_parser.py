import tempfile
from pathlib import Path
from typing import List

import fitz  # PyMuPDF: convert PDF pages to images


class PDFPageImage:
    def __init__(self, page_index: int, image_path: Path):
        self.page_index = page_index
        self.image_path = image_path


class PDFParser:
    def __init__(self, dpi: int = 300):
        self.dpi = dpi

    def pdf_to_images(self, pdf_path: str) -> List[PDFPageImage]:
        pdf = fitz.open(pdf_path)
        out: List[PDFPageImage] = []
        tmpdir = Path(tempfile.mkdtemp(prefix="pdf_pages_"))
        for i, page in enumerate(pdf):
            mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_path = tmpdir / f"page_{i+1:04d}.png"
            pix.save(str(img_path))
            out.append(PDFPageImage(page_index=i, image_path=img_path))
        return out
