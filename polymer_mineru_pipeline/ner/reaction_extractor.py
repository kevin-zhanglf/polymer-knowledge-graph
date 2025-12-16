import re
import uuid
from typing import List

from ..export.schemas import FormulaEntity, ReactionRelation, ChemicalEntity


ARROW_PATTERNS = [
    r"\\rightarrow",
    r"\\to",
    r"\\leftrightarrow",
]


class ReactionExtractor:
    def __init__(self):
        arrow_union = "|".join(ARROW_PATTERNS)
        self.re_arrow = re.compile(arrow_union)

    def is_reaction_formula(self, latex: str) -> bool:
        return bool(self.re_arrow.search(latex))

    def extract_from_formula(
        self,
        formula: FormulaEntity,
        all_chemicals: List[ChemicalEntity],
    ) -> List[ReactionRelation]:
        latex = formula.latex
        if not self.is_reaction_formula(latex):
            return []

        parts = self.re_arrow.split(latex)
        if len(parts) < 2:
            return []

        lhs, rhs = parts[0], parts[1]
        reactants_ids = []
        products_ids = []

        for chem in all_chemicals:
            if chem.context_id != formula.context_id:
                continue
            if chem.text in lhs:
                reactants_ids.append(chem.id)
            if chem.text in rhs:
                products_ids.append(chem.id)

        if not reactants_ids and not products_ids:
            return []

        reaction = ReactionRelation(
            id=str(uuid.uuid4()),
            reactants=list(set(reactants_ids)),
            products=list(set(products_ids)),
            conditions={},
            formula_id=formula.id,
        )
        return [reaction]
