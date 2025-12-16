from typing import List
import uuid

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

from ..config import NERConfig
from ..export.schemas import ChemicalEntity
from ..processing.normalizer import ChemNormalizer


CHEM_LABEL_MAPPING = {
    0: "O",
    1: "B-MONOMER",
    2: "I-MONOMER",
    3: "B-POLYMER",
    4: "I-POLYMER",
    5: "B-COMPOSITE",
    6: "I-COMPOSITE",
    7: "B-ADDITIVE",
    8: "I-ADDITIVE",
}


class ChemicalNER:
    def __init__(self, config: NERConfig):
        self.tokenizer = AutoTokenizer.from_pretrained(config.chem_model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(config.chem_model_name)
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        self.threshold = config.threshold
        self.chem_norm = ChemNormalizer()

    def _decode_entities(self, text: str, preds, page: int, context_id: str) -> List[ChemicalEntity]:
        entities: List[ChemicalEntity] = []
        current = None

        enc = self.tokenizer(
            text,
            return_offsets_mapping=True,
            truncation=True,
            return_tensors="pt",
        )
        offsets = enc["offset_mapping"][0].tolist()

        for label_id, (start, end) in zip(preds, offsets):
            if start == 0 and end == 0:
                continue
            label_name = CHEM_LABEL_MAPPING.get(int(label_id), "O")
            if label_name == "O":
                if current:
                    entities.append(current)
                    current = None
                continue

            prefix, etype = label_name.split("-", 1)
            span_text = text[start:end]

            if prefix == "B":
                if current:
                    entities.append(current)
                norm = self.chem_norm.normalize_chem_token(span_text)
                current = ChemicalEntity(
                    id=str(uuid.uuid4()),
                    text=span_text,
                    smiles=norm["smiles"],
                    entity_type=etype.lower(),
                    span={"start": start, "end": end},
                    context_id=context_id,
                    page=page,
                )
            elif prefix == "I" and current is not None and current.entity_type == etype.lower():
                current.text += text[start:end]
                current.span["end"] = end
            else:
                if current:
                    entities.append(current)
                norm = self.chem_norm.normalize_chem_token(span_text)
                current = ChemicalEntity(
                    id=str(uuid.uuid4()),
                    text=span_text,
                    smiles=norm["smiles"],
                    entity_type=etype.lower(),
                    span={"start": start, "end": end},
                    context_id=context_id,
                    page=page,
                )

        if current:
            entities.append(current)
        return entities

    @torch.no_grad()
    def infer_on_chunk(self, chunk_text: str, page: int, context_id: str) -> List[ChemicalEntity]:
        if not chunk_text.strip():
            return []
        enc = self.tokenizer(
            chunk_text,
            return_tensors="pt",
            truncation=True,
        ).to(self.device)
        outputs = self.model(**enc)
        logits = outputs.logits[0]
        preds = torch.argmax(logits, dim=-1).cpu().numpy().tolist()

        entities = self._decode_entities(chunk_text, preds, page, context_id)
        return entities
