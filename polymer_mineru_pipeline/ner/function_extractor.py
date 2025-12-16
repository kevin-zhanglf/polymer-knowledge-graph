import re
import uuid
from typing import List

from ..export.schemas import FormulaEntity, PropertyFunction


class FunctionExtractor:
    def __init__(self):
        self.property_regex = re.compile(
            r"(M_n|M_w|M_w/M_n|T_g|T_m|T_c|G'|G''|E'|E''|\\eta|D|k)", re.UNICODE
        )
        self.eq_regex = re.compile(r"(.+?)\s*=\s*(.+)")

    def extract_property_function(self, formula: FormulaEntity) -> List[PropertyFunction]:
        latex = formula.latex.strip().strip("$")
        m = self.eq_regex.match(latex)
        if not m:
            return []

        lhs, rhs = m.group(1), m.group(2)
        prop_match = self.property_regex.findall(lhs)
        if not prop_match:
            return []

        target_prop = prop_match[0]
        vars_candidates = set(re.findall(r"([A-Za-z]_\w+|[A-Za-z])", rhs))
        excluded = set()
        variables = [v for v in vars_candidates if v not in excluded]

        if not variables:
            return []

        return [
            PropertyFunction(
                id=str(uuid.uuid4()),
                formula_id=formula.id,
                target_property=target_prop,
                variables=variables,
                context_id=formula.context_id,
            )
        ]
