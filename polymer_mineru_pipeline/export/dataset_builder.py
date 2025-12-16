from pathlib import Path
import json
from typing import List

from .schemas import DocumentExample


class DatasetBuilder:
    def __init__(self, out_dir: str):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def write_jsonl(self, doc_examples: List[DocumentExample], filename: str = "dataset.jsonl"):
        out_path = self.out_dir / filename
        with out_path.open("w", encoding="utf-8") as f:
            for doc in doc_examples:
                f.write(json.dumps(doc.to_dict(), ensure_ascii=False) + "\n")
