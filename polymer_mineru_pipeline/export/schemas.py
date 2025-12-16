from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class FormulaEntity:
    id: str
    latex: str
    context_id: str   # corresponding chunk/paragraph ID
    page: int
    type: str         # "reaction", "kinetic", "empirical", "other"


@dataclass
class ChemicalEntity:
    id: str
    text: str
    smiles: Optional[str]
    entity_type: str  # "monomer", "polymer", "composite", "additive", etc.
    span: Dict[str, int]  # {"start": int, "end": int}
    context_id: str
    page: int


@dataclass
class ReactionRelation:
    id: str
    reactants: List[str]     # ChemicalEntity.id
    products: List[str]      # ChemicalEntity.id
    conditions: Dict[str, Any]  # temperature, catalyst, solvent, etc.
    formula_id: Optional[str]   # corresponding FormulaEntity.id (if any)


@dataclass
class PropertyFunction:
    id: str
    formula_id: str
    target_property: str     # e.g., "M_n", "M_w", "Tg", "viscosity"
    variables: List[str]     # e.g., ["conversion", "temperature"]
    context_id: str


@dataclass
class Chunk:
    id: str
    text: str
    page: int
    section: Optional[str]
    type: str                 # "paragraph", "table", "figure_caption", etc.
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentExample:
    doc_id: str
    chunks: List[Chunk] = field(default_factory=list)
    chemicals: List[ChemicalEntity] = field(default_factory=list)
    formulas: List[FormulaEntity] = field(default_factory=list)
    reactions: List[ReactionRelation] = field(default_factory=list)
    functions: List[PropertyFunction] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "chunks": [asdict(c) for c in self.chunks],
            "chemicals": [asdict(c) for c in self.chemicals],
            "formulas": [asdict(f) for f in self.formulas],
            "reactions": [asdict(r) for r in self.reactions],
            "functions": [asdict(f) for f in self.functions],
        }
