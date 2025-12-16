from typing import List
import uuid

from .config import PipelineConfig
from .parsing.pdf_parser import PDFParser
from .parsing.layout_analyzer import LayoutAnalyzer
from .parsing.ocr_math import OCRMathRecognizer
from .processing.normalizer import TextFormulaCleaner
from .processing.chunker import Chunker
from .ner.chem_ner import ChemicalNER
from .ner.reaction_extractor import ReactionExtractor
from .ner.function_extractor import FunctionExtractor
from .export.schemas import DocumentExample, Chunk, FormulaEntity, ChemicalEntity, ReactionRelation, PropertyFunction
from .export.dataset_builder import DatasetBuilder


class PolymerPipeline:
    def __init__(self, config: PipelineConfig, out_dir: str):
        self.config = config
        self.pdf_parser = PDFParser(dpi=config.ocr.dpi)
        self.layout_analyzer = LayoutAnalyzer(min_block_confidence=config.layout.min_block_confidence)
        self.ocr_math = OCRMathRecognizer(
            ocr_lang=config.ocr.language,
            math_model=config.ocr.math_ocr_model,
        )
        self.cleaner = TextFormulaCleaner()
        self.chunker = Chunker(
            max_tokens=config.chunk.max_tokens,
            keep_formula_with_paragraph=config.chunk.keep_formula_with_paragraph,
        )
        self.chem_ner = ChemicalNER(config.ner)
        self.reaction_extractor = ReactionExtractor()
        self.function_extractor = FunctionExtractor()
        self.dataset_builder = DatasetBuilder(out_dir=out_dir)

    def process_pdf(self, pdf_path: str, doc_id: str = None) -> DocumentExample:
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        pages = self.pdf_parser.pdf_to_images(pdf_path)
        layout_pages = self.layout_analyzer.analyze(pages)
        ocr_pages = [self.ocr_math.recognize_page_blocks(lp) for lp in layout_pages]

        doc = DocumentExample(doc_id=doc_id)
        formula_entities: List[FormulaEntity] = []

        for p in ocr_pages:
            page_index = p["page_index"]
            for b in p.get("blocks", []):
                if b.get("type") == "text":
                    raw = b.get("normalized_text", "") or ""
                    b["normalized_text"] = self.cleaner.clean_text(raw)
                elif b.get("type") == "formula":
                    raw = b.get("latex", "") or ""
                    b["latex"] = self.cleaner.clean_latex(raw)

            chunks = self.chunker.chunk_page(p)
            doc.chunks.extend(chunks)

            for b in p.get("blocks", []):
                if b.get("type") == "formula" and b.get("latex"):
                    fe = FormulaEntity(
                        id=str(uuid.uuid4()),
                        latex=b["latex"],
                        context_id=self._find_formula_chunk_id(chunks, b["latex"]),
                        page=page_index,
                        type="reaction" if self.reaction_extractor.is_reaction_formula(b["latex"]) else "other",
                    )
                    formula_entities.append(fe)

        doc.formulas.extend(formula_entities)

        all_chemicals: List[ChemicalEntity] = []
        for ch in doc.chunks:
            if ch.type not in ["paragraph", "formula"]:
                continue
            ents = self.chem_ner.infer_on_chunk(ch.text, ch.page, ch.id)
            all_chemicals.extend(ents)
        doc.chemicals.extend(all_chemicals)

        reactions: List[ReactionRelation] = []
        for fe in formula_entities:
            reactions.extend(self.reaction_extractor.extract_from_formula(fe, all_chemicals))
        doc.reactions.extend(reactions)

        functions: List[PropertyFunction] = []
        for fe in formula_entities:
            functions.extend(self.function_extractor.extract_property_function(fe))
        doc.functions.extend(functions)

        return doc

    def _find_formula_chunk_id(self, chunks: List[Chunk], latex: str) -> str:
        for ch in chunks:
            if latex in ch.text and ch.type == "formula":
                return ch.id
        return chunks[0].id if chunks else str(uuid.uuid4())

    def build_dataset(self, pdf_paths: List[str], output_name: str = "dataset.jsonl"):
        docs: List[DocumentExample] = []
        for path in pdf_paths:
            doc = self.process_pdf(path)
            docs.append(doc)
        self.dataset_builder.write_jsonl(docs, filename=output_name)
