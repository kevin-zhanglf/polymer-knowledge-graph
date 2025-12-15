"""
Base classes and dataclasses for PDF parsing and extraction.

This module provides core data structures and abstract base classes for PDF text,
table, and image extraction capabilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ElementType(Enum):
    """Enumeration of PDF element types."""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    SHAPE = "shape"
    UNKNOWN = "unknown"


@dataclass
class PDFMetadata:
    """Metadata information extracted from a PDF document."""
    
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    num_pages: int = 0
    pdf_version: Optional[str] = None
    is_encrypted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "title": self.title,
            "author": self.author,
            "subject": self.subject,
            "creator": self.creator,
            "producer": self.producer,
            "creation_date": self.creation_date,
            "modification_date": self.modification_date,
            "num_pages": self.num_pages,
            "pdf_version": self.pdf_version,
            "is_encrypted": self.is_encrypted,
        }


@dataclass
class TextElement:
    """Represents a text element in a PDF."""
    
    text: str
    page_num: int
    x0: float
    y0: float
    x1: float
    y1: float
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    is_bold: bool = False
    is_italic: bool = False
    confidence: float = 1.0
    element_type: ElementType = ElementType.TEXT
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        """Get bounding box as tuple (x0, y0, x1, y1)."""
        return (self.x0, self.y0, self.x1, self.y1)
    
    @property
    def width(self) -> float:
        """Get element width."""
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        """Get element height."""
        return self.y1 - self.y0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert text element to dictionary."""
        return {
            "text": self.text,
            "page_num": self.page_num,
            "bbox": self.bbox,
            "width": self.width,
            "height": self.height,
            "font_name": self.font_name,
            "font_size": self.font_size,
            "is_bold": self.is_bold,
            "is_italic": self.is_italic,
            "confidence": self.confidence,
            "element_type": self.element_type.value,
            "metadata": self.metadata,
        }


@dataclass
class TableElement:
    """Represents a table element in a PDF."""
    
    page_num: int
    x0: float
    y0: float
    x1: float
    y1: float
    rows: List[List[str]] = field(default_factory=list)
    num_rows: int = 0
    num_cols: int = 0
    confidence: float = 1.0
    cell_bboxes: List[List[Tuple[float, float, float, float]]] = field(default_factory=list)
    element_type: ElementType = ElementType.TABLE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        """Get bounding box as tuple (x0, y0, x1, y1)."""
        return (self.x0, self.y0, self.x1, self.y1)
    
    @property
    def width(self) -> float:
        """Get table width."""
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        """Get table height."""
        return self.y1 - self.y0
    
    def get_cell(self, row: int, col: int) -> Optional[str]:
        """Get cell content by row and column index."""
        if 0 <= row < len(self.rows) and 0 <= col < len(self.rows[row]):
            return self.rows[row][col]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table element to dictionary."""
        return {
            "page_num": self.page_num,
            "bbox": self.bbox,
            "width": self.width,
            "height": self.height,
            "rows": self.rows,
            "num_rows": self.num_rows,
            "num_cols": self.num_cols,
            "confidence": self.confidence,
            "element_type": self.element_type.value,
            "metadata": self.metadata,
        }


@dataclass
class ImageElement:
    """Represents an image element in a PDF."""
    
    page_num: int
    x0: float
    y0: float
    x1: float
    y1: float
    image_path: Optional[str] = None
    image_data: Optional[bytes] = None
    image_format: Optional[str] = None
    dpi: int = 72
    confidence: float = 1.0
    element_type: ElementType = ElementType.IMAGE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        """Get bounding box as tuple (x0, y0, x1, y1)."""
        return (self.x0, self.y0, self.x1, self.y1)
    
    @property
    def width(self) -> float:
        """Get image width."""
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        """Get image height."""
        return self.y1 - self.y0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert image element to dictionary."""
        return {
            "page_num": self.page_num,
            "bbox": self.bbox,
            "width": self.width,
            "height": self.height,
            "image_path": self.image_path,
            "image_format": self.image_format,
            "dpi": self.dpi,
            "confidence": self.confidence,
            "element_type": self.element_type.value,
            "metadata": self.metadata,
        }


@dataclass
class PDFPage:
    """Represents a single page in a PDF document."""
    
    page_num: int
    width: float
    height: float
    rotation: int = 0
    text_elements: List[TextElement] = field(default_factory=list)
    table_elements: List[TableElement] = field(default_factory=list)
    image_elements: List[ImageElement] = field(default_factory=list)
    raw_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def all_elements(self) -> List[Any]:
        """Get all elements from the page."""
        return self.text_elements + self.table_elements + self.image_elements
    
    def get_text(self) -> str:
        """Extract all text from the page."""
        if self.raw_text:
            return self.raw_text
        
        text_parts = [elem.text for elem in self.text_elements]
        return "\n".join(text_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert page to dictionary."""
        return {
            "page_num": self.page_num,
            "width": self.width,
            "height": self.height,
            "rotation": self.rotation,
            "num_text_elements": len(self.text_elements),
            "num_table_elements": len(self.table_elements),
            "num_image_elements": len(self.image_elements),
            "raw_text": self.raw_text,
            "metadata": self.metadata,
        }


@dataclass
class PDFDocument:
    """Represents a complete PDF document."""
    
    file_path: str
    metadata: PDFMetadata = field(default_factory=PDFMetadata)
    pages: List[PDFPage] = field(default_factory=list)
    
    @property
    def num_pages(self) -> int:
        """Get total number of pages."""
        return len(self.pages)
    
    def get_page(self, page_num: int) -> Optional[PDFPage]:
        """Get a specific page by number."""
        if 0 <= page_num < len(self.pages):
            return self.pages[page_num]
        return None
    
    def get_all_text_elements(self) -> List[TextElement]:
        """Get all text elements from all pages."""
        elements = []
        for page in self.pages:
            elements.extend(page.text_elements)
        return elements
    
    def get_all_table_elements(self) -> List[TableElement]:
        """Get all table elements from all pages."""
        elements = []
        for page in self.pages:
            elements.extend(page.table_elements)
        return elements
    
    def get_all_image_elements(self) -> List[ImageElement]:
        """Get all image elements from all pages."""
        elements = []
        for page in self.pages:
            elements.extend(page.image_elements)
        return elements
    
    def get_full_text(self) -> str:
        """Extract all text from the entire document."""
        text_parts = []
        for page in self.pages:
            text_parts.append(page.get_text())
        return "\n\n".join(text_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "file_path": self.file_path,
            "num_pages": self.num_pages,
            "metadata": self.metadata.to_dict(),
            "pages": [page.to_dict() for page in self.pages],
        }


class BasePDFExtractor(ABC):
    """Abstract base class for PDF extraction."""
    
    def __init__(self, file_path: str):
        """
        Initialize the PDF extractor.
        
        Args:
            file_path: Path to the PDF file to extract from.
        """
        self.file_path = file_path
        self.document: Optional[PDFDocument] = None
    
    @abstractmethod
    def extract(self) -> PDFDocument:
        """
        Extract content from PDF file.
        
        Returns:
            PDFDocument: The extracted PDF document with all content.
        """
        pass
    
    @abstractmethod
    def extract_text(self) -> List[TextElement]:
        """
        Extract text elements from PDF.
        
        Returns:
            List[TextElement]: List of extracted text elements.
        """
        pass
    
    @abstractmethod
    def extract_tables(self) -> List[TableElement]:
        """
        Extract table elements from PDF.
        
        Returns:
            List[TableElement]: List of extracted table elements.
        """
        pass
    
    @abstractmethod
    def extract_images(self) -> List[ImageElement]:
        """
        Extract image elements from PDF.
        
        Returns:
            List[ImageElement]: List of extracted image elements.
        """
        pass
    
    @abstractmethod
    def extract_metadata(self) -> PDFMetadata:
        """
        Extract metadata from PDF.
        
        Returns:
            PDFMetadata: The PDF metadata.
        """
        pass


class SimpleTextExtractor(BasePDFExtractor):
    """Simple PDF extractor that extracts text only."""
    
    def __init__(self, file_path: str):
        """
        Initialize the simple text extractor.
        
        Args:
            file_path: Path to the PDF file to extract from.
        """
        super().__init__(file_path)
    
    def extract(self) -> PDFDocument:
        """
        Extract text content from PDF file.
        
        Returns:
            PDFDocument: The extracted PDF document with text elements.
            
        Raises:
            NotImplementedError: This method requires a PDF library implementation.
        """
        raise NotImplementedError(
            "SimpleTextExtractor requires PyPDF2 or pdfplumber to be installed and configured."
        )
    
    def extract_text(self) -> List[TextElement]:
        """
        Extract text elements from PDF.
        
        Returns:
            List[TextElement]: List of extracted text elements.
            
        Raises:
            NotImplementedError: This method requires a PDF library implementation.
        """
        raise NotImplementedError(
            "Text extraction requires a PDF library implementation."
        )
    
    def extract_tables(self) -> List[TableElement]:
        """
        Extract table elements from PDF.
        
        Returns:
            List[TableElement]: Empty list (not supported by SimpleTextExtractor).
        """
        return []
    
    def extract_images(self) -> List[ImageElement]:
        """
        Extract image elements from PDF.
        
        Returns:
            List[ImageElement]: Empty list (not supported by SimpleTextExtractor).
        """
        return []
    
    def extract_metadata(self) -> PDFMetadata:
        """
        Extract metadata from PDF.
        
        Returns:
            PDFMetadata: The PDF metadata.
            
        Raises:
            NotImplementedError: This method requires a PDF library implementation.
        """
        raise NotImplementedError(
            "Metadata extraction requires a PDF library implementation."
        )


class AdvancedPDFExtractor(BasePDFExtractor):
    """Advanced PDF extractor that extracts text, tables, and images."""
    
    def __init__(
        self,
        file_path: str,
        extract_tables: bool = True,
        extract_images: bool = True,
        table_settings: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the advanced PDF extractor.
        
        Args:
            file_path: Path to the PDF file to extract from.
            extract_tables: Whether to extract tables from the PDF.
            extract_images: Whether to extract images from the PDF.
            table_settings: Optional dictionary with table extraction settings.
        """
        super().__init__(file_path)
        self.extract_tables_flag = extract_tables
        self.extract_images_flag = extract_images
        self.table_settings = table_settings or {}
    
    def extract(self) -> PDFDocument:
        """
        Extract all content from PDF file.
        
        Returns:
            PDFDocument: The extracted PDF document with all content.
            
        Raises:
            NotImplementedError: This method requires a PDF library implementation.
        """
        raise NotImplementedError(
            "AdvancedPDFExtractor requires pdfplumber or similar library to be installed and configured."
        )
    
    def extract_text(self) -> List[TextElement]:
        """
        Extract text elements from PDF.
        
        Returns:
            List[TextElement]: List of extracted text elements.
            
        Raises:
            NotImplementedError: This method requires a PDF library implementation.
        """
        raise NotImplementedError(
            "Text extraction requires a PDF library implementation."
        )
    
    def extract_tables(self) -> List[TableElement]:
        """
        Extract table elements from PDF.
        
        Returns:
            List[TableElement]: List of extracted table elements.
            
        Raises:
            NotImplementedError: This method requires a PDF library implementation.
        """
        if not self.extract_tables_flag:
            return []
        
        raise NotImplementedError(
            "Table extraction requires pdfplumber or similar library to be installed and configured."
        )
    
    def extract_images(self) -> List[ImageElement]:
        """
        Extract image elements from PDF.
        
        Returns:
            List[ImageElement]: List of extracted image elements.
            
        Raises:
            NotImplementedError: This method requires a PDF library implementation.
        """
        if not self.extract_images_flag:
            return []
        
        raise NotImplementedError(
            "Image extraction requires pdfplumber or similar library to be installed and configured."
        )
    
    def extract_metadata(self) -> PDFMetadata:
        """
        Extract metadata from PDF.
        
        Returns:
            PDFMetadata: The PDF metadata.
            
        Raises:
            NotImplementedError: This method requires a PDF library implementation.
        """
        raise NotImplementedError(
            "Metadata extraction requires a PDF library implementation."
        )
    
    def set_table_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update table extraction settings.
        
        Args:
            settings: Dictionary with table extraction settings.
        """
        self.table_settings.update(settings)
