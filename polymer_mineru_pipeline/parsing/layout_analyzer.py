from typing import List, Dict, Any

from .pdf_parser import PDFPageImage


class LayoutAnalyzer:
    """Wrapper for layout analysis (e.g. via MinerU).

    Replace the body of `analyze` with an actual MinerU call that returns page
    blocks with type + bbox + optional raw_ocr or cropped images.
    """

    def __init__(self, min_block_confidence: float = 0.5):
        self.min_block_confidence = min_block_confidence

    def analyze(self, pages: List[PDFPageImage]) -> List[Dict[str, Any]]:
        """Return per-page layout structure.

        Expected format:
        [
          {
            "page_index": 0,
            "blocks": [
              {
                "id": "p0_b0",
                "bbox": [x1, y1, x2, y2],
                "type": "text" | "formula" | "table" | "figure",
                "image_path": "...",   # if you crop image regions
                "raw_ocr": "...",      # initial OCR text if available
              },
              ...
            ]
          },
          ...
        ]
        """
        # TODO: replace with MinerU-based implementation.
        results: List[Dict[str, Any]] = []
        for p in pages:
            results.append(
                {
                    "page_index": p.page_index,
                    "blocks": [],  # populate with real layout blocks
                }
            )
        return results
