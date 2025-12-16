import uuid
from typing import List, Dict, Any

from ..export.schemas import Chunk


class Chunker:
    def __init__(self, max_tokens: int = 512, keep_formula_with_paragraph: bool = True):
        self.max_tokens = max_tokens
        self.keep_formula_with_paragraph = keep_formula_with_paragraph

    def _estimate_tokens(self, text: str) -> int:
        return len(text.split())

    def chunk_page(self, page: Dict[str, Any]) -> List[Chunk]:
        page_index = page["page_index"]
        text_blocks = [b for b in page.get("blocks", []) if b.get("type") == "text"]
        formula_blocks = [b for b in page.get("blocks", []) if b.get("type") == "formula"]
        chunks: List[Chunk] = []

        current_text = ""
        for tb in text_blocks:
            t = tb.get("normalized_text", "").strip()
            if not t:
                continue

            est_tokens_after = self._estimate_tokens(current_text + " " + t)
            if est_tokens_after > self.max_tokens and current_text:
                chunks.append(
                    Chunk(
                        id=str(uuid.uuid4()),
                        text=current_text.strip(),
                        page=page_index,
                        section=None,
                        type="paragraph",
                        meta={},
                    )
                )
                current_text = t
            else:
                current_text += " " + t

        if current_text:
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    text=current_text.strip(),
                    page=page_index,
                    section=None,
                    type="paragraph",
                    meta={},
                )
            )

        for fb in formula_blocks:
            formula_text = fb.get("latex", "")
            if not formula_text:
                continue
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    text=formula_text,
                    page=page_index,
                    section=None,
                    type="formula",
                    meta={"block_id": fb.get("id")},
                )
            )

        return chunks
