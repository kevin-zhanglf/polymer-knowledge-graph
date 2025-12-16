from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OCRConfig:
    language: str = "eng"
    math_ocr_model: str = "trivial-latex-ocr"  # replace with your formula recognition model ID
    dpi: int = 300


@dataclass
class LayoutConfig:
    min_block_confidence: float = 0.5
    merge_headers: bool = True
    remove_page_footer: bool = True


@dataclass
class ChunkConfig:
    max_tokens: int = 512
    sentence_overlap: int = 1
    keep_formula_with_paragraph: bool = True
    keep_tables: bool = True


@dataclass
class NERConfig:
    chem_model_name: str = "allenai/scibert_scivocab_cased"  # can be replaced by chemical-domain NER model
    device: str = "cuda:0"
    batch_size: int = 8
    threshold: float = 0.5


@dataclass
class PipelineConfig:
    ocr: OCRConfig = field(default_factory=OCRConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    chunk: ChunkConfig = field(default_factory=ChunkConfig)
    ner: NERConfig = field(default_factory=NERConfig)
