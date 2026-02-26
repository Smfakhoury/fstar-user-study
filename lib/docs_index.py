"""
F* Documentation and Example Index

Provides searchable access to F* library documentation, lemmas, and examples.
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class LemmaInfo:
    """Information about an F* lemma or function"""
    name: str
    module: str
    signature: str
    body: str
    doc: str = ""


@dataclass
class ExampleInfo:
    """Information about an F* code example"""
    name: str
    source_file: str
    code: str
    description: str = ""


class FStarDocsIndex:
    """Index of F* documentation, lemmas, and examples"""

    def __init__(self, docs_dir: Path = None, examples_dir: Path = None):
        self.docs_dir = docs_dir or Path(__file__).parent.parent / "docs"
        self.examples_dir = examples_dir or Path(__file__).parent.parent / "examples"
        self.lemmas: dict[str, LemmaInfo] = {}
        self.examples: list[ExampleInfo] = []
        self._index_stdlib()
        self._index_examples()

    def _index_stdlib(self):
        """Index F* standard library lemmas and functions"""
        stdlib_dir = self.examples_dir / "stdlib"
        if not stdlib_dir.exists():
            return

        for fst_file in stdlib_dir.glob("*.fst"):
            module_name = fst_file.stem
            content = fst_file.read_text()

            # Extract val declarations (function signatures)
            val_pattern = r'val\s+(\w+)\s*:\s*([^=]+?)(?=\nlet|\nval|\n\n|$)'
            for match in re.finditer(val_pattern, content, re.DOTALL):
                name = match.group(1)
                signature = match.group(2).strip()

                # Find corresponding let binding
                let_pattern = rf'let\s+(?:rec\s+)?{name}\b[^=]*=\s*(.*?)(?=\nlet|\nval|\n\n|$)'
                let_match = re.search(let_pattern, content, re.DOTALL)
                body = let_match.group(1).strip() if let_match else ""

                self.lemmas[f"{module_name}.{name}"] = LemmaInfo(
                    name=name,
                    module=module_name,
                    signature=signature,
                    body=body[:500]  # Truncate long bodies
                )

    def _index_examples(self):
        """Index example F* files"""
        # Index ground truth solutions
        gt_dir = self.examples_dir.parent / "ground-truth"
        if gt_dir.exists():
            for fst_file in gt_dir.glob("*.fst"):
                content = fst_file.read_text()
                # Extract description from comments
                desc_match = re.search(r'//\s*\[?\d*\]?\s*(.+)', content)
                desc = desc_match.group(1) if desc_match else fst_file.stem

                self.examples.append(ExampleInfo(
                    name=fst_file.stem,
                    source_file=str(fst_file),
                    code=content,
                    description=desc
                ))

    def search_lemmas(self, query: str, limit: int = 5) -> list[LemmaInfo]:
        """Search for lemmas matching a query"""
        query_lower = query.lower()
        results = []

        for full_name, lemma in self.lemmas.items():
            score = 0
            # Score based on name match
            if query_lower in lemma.name.lower():
                score += 10
            # Score based on signature match
            if query_lower in lemma.signature.lower():
                score += 5
            # Score based on module match
            if query_lower in lemma.module.lower():
                score += 3

            if score > 0:
                results.append((score, lemma))

        results.sort(key=lambda x: -x[0])
        return [r[1] for r in results[:limit]]

    def search_examples(self, query: str, limit: int = 3) -> list[ExampleInfo]:
        """Search for examples matching a query"""
        query_lower = query.lower()
        results = []

        for example in self.examples:
            score = 0
            if query_lower in example.description.lower():
                score += 10
            if query_lower in example.code.lower():
                score += 5
            if query_lower in example.name.lower():
                score += 3

            if score > 0:
                results.append((score, example))

        results.sort(key=lambda x: -x[0])
        return [r[1] for r in results[:limit]]

    def get_module_functions(self, module: str) -> list[LemmaInfo]:
        """Get all functions from a module"""
        return [l for l in self.lemmas.values() if module.lower() in l.module.lower()]

    def get_lemma(self, name: str) -> Optional[LemmaInfo]:
        """Get a specific lemma by name"""
        # Try exact match
        if name in self.lemmas:
            return self.lemmas[name]
        # Try partial match
        for full_name, lemma in self.lemmas.items():
            if name == lemma.name or name in full_name:
                return lemma
        return None


# Singleton instance
_index: Optional[FStarDocsIndex] = None

def get_docs_index() -> FStarDocsIndex:
    """Get the global docs index"""
    global _index
    if _index is None:
        _index = FStarDocsIndex()
    return _index
