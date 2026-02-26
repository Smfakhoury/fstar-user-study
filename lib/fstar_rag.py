#!/usr/bin/env python3
"""
F* Retrieval-Augmented Generation (RAG) for lemma lookup.

Indexes F* stdlib and provides semantic search for relevant lemmas.
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FStarDefinition:
    name: str
    module: str
    kind: str  # val, let, lemma, type
    signature: str
    body: str
    file_path: str
    line_number: int

class FStarRAG:
    def __init__(self, cache_path: str = ".fstar_index.json"):
        self.cache_path = Path(cache_path)
        self.definitions: List[FStarDefinition] = []
        self._load_or_build_index()

    def _load_or_build_index(self):
        if self.cache_path.exists():
            self._load_index()
        else:
            self._build_index()
            self._save_index()

    def _build_index(self):
        """Index common F* patterns and stdlib signatures."""
        # Core patterns that experts use frequently
        self.definitions = [
            # List operations
            FStarDefinition("mem", "FStar.List.Tot", "val",
                "val mem: #a:eqtype -> a -> list a -> bool",
                "Returns true if element is in list", "", 0),
            FStarDefinition("length", "FStar.List.Tot", "val",
                "val length: #a:Type -> list a -> nat",
                "Returns length of list", "", 0),
            FStarDefinition("index", "FStar.List.Tot", "val",
                "val index: #a:Type -> l:list a -> i:nat{i < length l} -> a",
                "Returns element at index i", "", 0),
            FStarDefinition("append", "FStar.List.Tot", "val",
                "val append: #a:Type -> list a -> list a -> list a",
                "Concatenates two lists", "", 0),
            FStarDefinition("filter", "FStar.List.Tot", "val",
                "val filter: #a:Type -> (a -> bool) -> list a -> list a",
                "Filters list by predicate", "", 0),

            # List lemmas
            FStarDefinition("mem_append", "FStar.List.Tot.Properties", "lemma",
                "val mem_append: #a:eqtype -> x:a -> l1:list a -> l2:list a -> Lemma (mem x (append l1 l2) <==> mem x l1 \\/ mem x l2)",
                "Membership distributes over append", "", 0),
            FStarDefinition("length_append", "FStar.List.Tot.Properties", "lemma",
                "val length_append: #a:Type -> l1:list a -> l2:list a -> Lemma (length (append l1 l2) == length l1 + length l2)",
                "Length of append is sum of lengths", "", 0),

            # Seq operations
            FStarDefinition("Seq.length", "FStar.Seq", "val",
                "val length: #a:Type -> seq a -> nat",
                "Returns length of sequence", "", 0),
            FStarDefinition("Seq.index", "FStar.Seq", "val",
                "val index: #a:Type -> s:seq a -> i:nat{i < length s} -> a",
                "Returns element at index (O(1))", "", 0),
            FStarDefinition("Seq.slice", "FStar.Seq", "val",
                "val slice: #a:Type -> s:seq a -> i:nat -> j:nat{i <= j /\\ j <= length s} -> seq a",
                "Returns subsequence from i to j", "", 0),
            FStarDefinition("Seq.create", "FStar.Seq", "val",
                "val create: #a:Type -> n:nat -> a -> seq a",
                "Creates sequence of n copies of element", "", 0),
            FStarDefinition("Seq.append", "FStar.Seq", "val",
                "val append: #a:Type -> seq a -> seq a -> seq a",
                "Concatenates two sequences", "", 0),

            # Seq lemmas
            FStarDefinition("lemma_index_slice", "FStar.Seq.Properties", "lemma",
                "val lemma_index_slice: #a:Type -> s:seq a -> i:nat -> j:nat{i <= j /\\ j <= length s} -> k:nat{k < j - i} -> Lemma (index (slice s i j) k == index s (i + k))",
                "Indexing into a slice", "", 0),
            FStarDefinition("lemma_len_slice", "FStar.Seq.Properties", "lemma",
                "val lemma_len_slice: #a:Type -> s:seq a -> i:nat -> j:nat{i <= j /\\ j <= length s} -> Lemma (length (slice s i j) == j - i)",
                "Length of a slice", "", 0),

            # Common proof patterns
            FStarDefinition("assert_norm", "FStar.Pervasives", "val",
                "val assert_norm: p:Type0 -> Pure unit (requires (normalize p)) (ensures (fun _ -> p))",
                "Assert with normalization - useful for concrete computations", "", 0),
            FStarDefinition("admit", "FStar.Pervasives", "val",
                "val admit: unit -> Admit 'a",
                "Skip proof obligation (use to defer verification)", "", 0),
            FStarDefinition("assume", "FStar.Pervasives", "val",
                "val assume: p:Type0 -> Pure unit (requires True) (ensures (fun _ -> p))",
                "Assume a fact without proving it", "", 0),
        ]

    def _load_index(self):
        with open(self.cache_path) as f:
            data = json.load(f)
            self.definitions = [FStarDefinition(**d) for d in data]

    def _save_index(self):
        with open(self.cache_path, 'w') as f:
            json.dump([d.__dict__ for d in self.definitions], f, indent=2)

    def search(self, query: str, limit: int = 5) -> List[FStarDefinition]:
        """Search for definitions matching query."""
        query_words = set(query.lower().split())
        scored = []

        for defn in self.definitions:
            # Score based on word overlap
            text = f"{defn.name} {defn.signature} {defn.body}".lower()
            text_words = set(re.findall(r'\w+', text))
            overlap = len(query_words & text_words)

            # Boost exact name matches
            if query.lower() in defn.name.lower():
                overlap += 5

            if overlap > 0:
                scored.append((overlap, defn))

        scored.sort(key=lambda x: -x[0])
        return [d for _, d in scored[:limit]]

    def get_relevant_for_task(self, task_description: str) -> List[FStarDefinition]:
        """Get definitions relevant to a proof task."""
        # Keyword-based relevance
        keywords = []
        task_lower = task_description.lower()

        if any(w in task_lower for w in ["list", "array", "element"]):
            keywords.extend(["mem", "length", "index", "filter"])
        if any(w in task_lower for w in ["seq", "sequence", "position"]):
            keywords.extend(["Seq.length", "Seq.index", "Seq.slice"])
        if any(w in task_lower for w in ["append", "concat", "join"]):
            keywords.extend(["append", "length_append", "mem_append"])
        if any(w in task_lower for w in ["max", "min", "largest", "smallest"]):
            keywords.extend(["mem", "length"])
        if any(w in task_lower for w in ["search", "find", "binary"]):
            keywords.extend(["Seq.index", "Seq.length"])
        if any(w in task_lower for w in ["sublist", "subsequence", "contiguous"]):
            keywords.extend(["Seq.slice", "lemma_index_slice", "lemma_len_slice"])

        results = []
        for kw in keywords:
            results.extend(self.search(kw, limit=2))

        # Deduplicate
        seen = set()
        unique = []
        for d in results:
            if d.name not in seen:
                seen.add(d.name)
                unique.append(d)

        return unique[:10]


# CLI interface
if __name__ == "__main__":
    import sys
    rag = FStarRAG()

    if len(sys.argv) < 2:
        print("Usage: python fstar_rag.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    results = rag.search(query)

    print(f"Results for '{query}':\n")
    for defn in results:
        print(f"  {defn.module}.{defn.name}")
        print(f"    {defn.signature}")
        print(f"    {defn.body}\n")
