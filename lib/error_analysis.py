#!/usr/bin/env python3
"""
Smart Error Analysis for F* Verification

Instead of blind iteration, analyze errors and suggest targeted fixes.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ErrorAnalysis:
    error_type: str
    location: str
    root_cause: str
    fix_strategy: str
    code_hint: Optional[str] = None

def analyze_error(error_text: str) -> ErrorAnalysis:
    """Analyze an F* error and suggest a fix strategy."""

    # Subtyping / refinement failure
    if "Subtyping check failed" in error_text:
        if "nat" in error_text and "int" in error_text:
            return ErrorAnalysis(
                error_type="refinement_nat",
                location=_extract_location(error_text),
                root_cause="Trying to use int where nat required (non-negative)",
                fix_strategy="Add bounds check or strengthen precondition",
                code_hint="if x >= 0 then ... else ..."
            )
        elif "length" in error_text or "index" in error_text:
            return ErrorAnalysis(
                error_type="refinement_bounds",
                location=_extract_location(error_text),
                root_cause="Array/sequence index might be out of bounds",
                fix_strategy="Add bounds check or prove index < length",
                code_hint="if i < length s then index s i else ..."
            )
        else:
            return ErrorAnalysis(
                error_type="refinement_general",
                location=_extract_location(error_text),
                root_cause="Refinement type constraint not satisfied",
                fix_strategy="Add assertion before use, or strengthen preconditions",
                code_hint="assert (property); ..."
            )

    # SMT solver couldn't prove
    if "Could not prove" in error_text or "SMT solver could not prove" in error_text:
        if "termination" in error_text.lower():
            return ErrorAnalysis(
                error_type="termination",
                location=_extract_location(error_text),
                root_cause="Recursive function doesn't have decreasing measure",
                fix_strategy="Add (decreases <measure>) clause",
                code_hint="let rec f ... : Tot _ (decreases (hi - lo)) = ..."
            )
        elif "forall" in error_text or "exists" in error_text:
            return ErrorAnalysis(
                error_type="quantifier",
                location=_extract_location(error_text),
                root_cause="Quantified property not provable by SMT",
                fix_strategy="Add intermediate assertion or invoke lemma",
                code_hint="assert (forall x. P x); // or call lemma"
            )
        else:
            return ErrorAnalysis(
                error_type="smt_failure",
                location=_extract_location(error_text),
                root_cause="SMT solver needs more hints",
                fix_strategy="Break into smaller steps with assertions",
                code_hint="assert (step1); assert (step2); ..."
            )

    # Incomplete patterns
    if "Patterns are incomplete" in error_text:
        return ErrorAnalysis(
            error_type="incomplete_match",
            location=_extract_location(error_text),
            root_cause="Match expression doesn't cover all cases",
            fix_strategy="Add precondition (e.g., length > 0) or handle empty case",
            code_hint="match l with | [] -> ... | hd :: tl -> ..."
        )

    # Identifier not found
    if "Identifier not found" in error_text:
        match = re.search(r'\[(\w+)\]', error_text)
        ident = match.group(1) if match else "unknown"
        return ErrorAnalysis(
            error_type="undefined",
            location=_extract_location(error_text),
            root_cause=f"Identifier '{ident}' not defined or imported",
            fix_strategy=f"Add 'open' statement or define '{ident}'",
            code_hint=f"open FStar.List.Tot // if {ident} is from stdlib"
        )

    # Type mismatch
    if "Expected type" in error_text and "got type" in error_text:
        return ErrorAnalysis(
            error_type="type_mismatch",
            location=_extract_location(error_text),
            root_cause="Expression has wrong type",
            fix_strategy="Check types match, may need coercion",
            code_hint="// Check expected vs actual types in error"
        )

    # Module declaration mismatch
    if "module declaration" in error_text:
        return ErrorAnalysis(
            error_type="module_name",
            location=_extract_location(error_text),
            root_cause="Module name doesn't match filename",
            fix_strategy="Rename module to match filename",
            code_hint="module <Filename> // without .fst"
        )

    # Default
    return ErrorAnalysis(
        error_type="unknown",
        location=_extract_location(error_text),
        root_cause="Unrecognized error pattern",
        fix_strategy="Read error message carefully, check F* documentation",
        code_hint=None
    )


def _extract_location(error_text: str) -> str:
    """Extract file location from error."""
    match = re.search(r'at [^(]+\((\d+),(\d+)', error_text)
    if match:
        return f"line {match.group(1)}, col {match.group(2)}"
    return "unknown location"


def analyze_all_errors(output: str) -> List[ErrorAnalysis]:
    """Analyze all errors in F* output."""
    # Split by error markers
    errors = re.split(r'\* Error \d+', output)
    analyses = []

    for err in errors[1:]:  # Skip first empty split
        analyses.append(analyze_error(err))

    return analyses


def suggest_bounded_errors_strategy(analyses: List[ErrorAnalysis]) -> str:
    """
    Suggest strategy for keeping errors bounded (paper finding: ≤4 active errors).
    """
    if len(analyses) <= 4:
        return "Error count OK. Fix errors in order of: termination > type > refinement"

    # Too many errors - suggest deferral
    by_type = {}
    for a in analyses:
        by_type.setdefault(a.error_type, []).append(a)

    lines = [
        f"WARNING: {len(analyses)} active errors (recommended: ≤4)",
        "",
        "STRATEGY: Use assume/admit to defer verification on parts of the code",
        ""
    ]

    # Prioritize which to fix first
    if "termination" in by_type:
        lines.append("1. FIX FIRST: Termination errors (add decreases clauses)")
    if "incomplete_match" in by_type:
        lines.append("2. FIX SECOND: Incomplete patterns (add preconditions)")
    if "undefined" in by_type:
        lines.append("3. FIX THIRD: Undefined identifiers (add opens)")

    lines.extend([
        "",
        "For remaining errors, comment out code sections or use:",
        "  assume (property_to_prove_later);",
        "  admit (); // skip this proof obligation",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    # Test with sample error
    sample = """
* Error 19 at /workspace/test.fst(10,5-10,15):
  - Subtyping check failed
  - Expected type i: Prims.nat{i < FStar.Seq.Base.length s}
    got type Prims.int
  - The SMT solver could not prove the query.
"""
    analysis = analyze_error(sample)
    print(f"Type: {analysis.error_type}")
    print(f"Location: {analysis.location}")
    print(f"Root cause: {analysis.root_cause}")
    print(f"Fix strategy: {analysis.fix_strategy}")
    print(f"Code hint: {analysis.code_hint}")
