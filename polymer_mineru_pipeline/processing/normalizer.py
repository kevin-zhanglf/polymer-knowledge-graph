import re
from typing import Dict, Any, Optional

from rdkit import Chem
from rdkit.Chem import MolToSmiles


class ChemNormalizer:
    """Normalize chemical tokens to SMILES where possible."""

    def __init__(self):
        pass

    def name_to_smiles(self, name: str) -> Optional[str]:
        # TODO: connect to external name-to-structure services (OPSIN, PubChem, etc.)
        try:
            mol = Chem.MolFromSmiles(name)
            if mol:
                return MolToSmiles(mol)
        except Exception:
            return None
        return None

    def normalize_chem_token(self, token: str) -> Dict[str, Any]:
        smiles = self.name_to_smiles(token)
        return {
            "text": token,
            "smiles": smiles,
        }


class TextFormulaCleaner:
    """Clean and normalize plain text and LaTeX formulas."""

    LATEX_FIXES = [
        (r"\\\mathrm\{([A-Za-z]+)\}", r"\\text{\1}"),
        (r"(\d)\s+(\d)", r"\1\2"),
        (r"\\\s+", r"\\"),
    ]

    def clean_text(self, text: str) -> str:
        text = re.sub(r"^\s*Page\s+\d+.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"-+\s*\d+\s*-+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def clean_latex(self, latex: str) -> str:
        result = latex
        for pattern, repl in self.LATEX_FIXES:
            result = re.sub(pattern, repl, result)
        result = result.strip()
        if not (result.startswith("$") and result.endswith("$")):
            result = f"${result}$"
        return result
