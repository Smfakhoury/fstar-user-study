#!/usr/bin/env python3
"""
F* Proof Tools - CLI tools for proof development

These tools can be invoked by Claude Code to assist with F* proof development.
Each tool performs a specific function and returns structured output.

Usage:
    python fstar_tools.py <command> [args]

Commands:
    analyze <task>           - Analyze a task and suggest approach
    search-lemmas <query>    - Search for relevant lemmas
    search-examples <query>  - Search for relevant examples
    verify <file>            - Verify an F* file
    get-errors <file>        - Get detailed error analysis
    suggest-fix <file>       - Suggest fixes for errors
"""

import subprocess
import os
import re
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from docs_index import get_docs_index


def cmd_analyze(task: str) -> dict:
    """Analyze a proof task and suggest approach"""
    task_lower = task.lower()

    result = {
        "task": task,
        "representation_choice": {},  # NEW: First-class representation decision
        "data_structures": [],
        "operations": [],
        "suggested_approach": [],
        "suggested_modules": [],
        "complexity_notes": []
    }

    # STEP 0: Representation choice (critical first decision per paper findings)
    # "Experts deliberated on the most suitable representation, balancing efficiency with proof complexity"

    # Use word boundary matching to avoid false positives (e.g., "duplicates" containing "at")
    import re
    def has_word(text, words):
        return any(re.search(r'\b' + re.escape(w) + r'\b', text) for w in words)

    needs_indexing = has_word(task_lower, ["index", "position", "at", "search", "binary", "sublist", "subsequence"])
    needs_membership = has_word(task_lower, ["contains", "member", "intersection", "filter"]) or " in " in task_lower
    needs_ordering = has_word(task_lower, ["sorted", "order", "max", "min", "largest", "smallest"])
    needs_mutation = has_word(task_lower, ["update", "modify", "change", "set"])

    result["representation_choice"] = {
        "recommendation": None,
        "alternatives": [],
        "tradeoffs": []
    }

    if needs_indexing:
        result["representation_choice"]["recommendation"] = "Seq"
        result["representation_choice"]["tradeoffs"] = [
            "Seq: O(1) indexing, cleaner index proofs, better for position-based specs",
            "List: O(n) indexing, but pattern matching is more natural for recursion"
        ]
        result["representation_choice"]["alternatives"] = ["List (if recursive structure preferred)"]
    elif needs_membership:
        result["representation_choice"]["recommendation"] = "List"
        result["representation_choice"]["tradeoffs"] = [
            "List: Built-in 'mem'/'contains', natural for filter/map operations",
            "Seq: Need to quantify over indices for membership"
        ]
        result["representation_choice"]["alternatives"] = ["Seq (if also need indexing)"]
    elif needs_ordering:
        result["representation_choice"]["recommendation"] = "List"
        result["representation_choice"]["tradeoffs"] = [
            "List: Natural recursive structure for max/min proofs",
            "Seq: Better if also need random access"
        ]
        result["representation_choice"]["alternatives"] = ["Seq"]
    else:
        result["representation_choice"]["recommendation"] = "List"
        result["representation_choice"]["tradeoffs"] = [
            "List: Default choice, good for most recursive algorithms",
            "Seq: Consider if random access or slicing needed"
        ]

    # Also consider quantifier choice
    result["representation_choice"]["quantifier_notes"] = []
    if "all" in task_lower or "every" in task_lower or "each" in task_lower:
        result["representation_choice"]["quantifier_notes"].append(
            "Use 'forall' - may need to rewrite in terms of indices if SMT struggles"
        )
    if "some" in task_lower or "exists" in task_lower or "find" in task_lower:
        result["representation_choice"]["quantifier_notes"].append(
            "Existentials need witnesses - consider returning the index/element explicitly"
        )

    # Detect data structures
    if any(w in task_lower for w in ["list", "array"]):
        result["data_structures"].append("list")
        result["suggested_modules"].append("FStar.List.Tot")
        result["suggested_modules"].append("FStar.List.Tot.Properties")

    if any(w in task_lower for w in ["seq", "sequence", "vector"]):
        result["data_structures"].append("seq")
        result["suggested_modules"].append("FStar.Seq")
        result["suggested_modules"].append("FStar.Seq.Properties")

    # Detect operations and suggest approach
    if any(w in task_lower for w in ["binary", "search"]) and "sorted" in task_lower:
        result["operations"].append("binary_search")
        result["suggested_approach"].extend([
            "1. Define 'is_sorted' predicate",
            "2. Define search function with refinement type for result",
            "3. Use recursive helper with bounds and decreases clause",
            "4. Prove: if result >= 0, element at that index equals target",
            "5. Prove: if result < 0, target not in list"
        ])
        result["complexity_notes"].append("Need termination proof via decreasing measure (hi - lo)")

    if any(w in task_lower for w in ["intersect"]):
        result["operations"].append("intersection")
        result["suggested_approach"].extend([
            "1. Define spec: forall x. mem x result <==> mem x a /\\ mem x b",
            "2. Use filter or recursive implementation",
            "3. Use 'contains' from FStar.List.Tot",
            "4. Recursively process first list, checking membership in second"
        ])

    if any(w in task_lower for w in ["max", "largest"]) and any(w in task_lower for w in ["min", "smallest", "diff"]):
        result["operations"].append("max_min_difference")
        result["suggested_approach"].extend([
            "1. Define max_list: recursively find maximum",
            "2. Define min_list: recursively find minimum",
            "3. Prove lemma: max_list >= min_list (by induction)",
            "4. Return max_list - min_list with refinement r:int{r >= 0}"
        ])
        result["complexity_notes"].append("Need lemma proving max >= min for the refinement type")

    if any(w in task_lower for w in ["sublist", "subsequence", "contains"]):
        result["operations"].append("sublist_check")
        result["suggested_approach"].extend([
            "1. Define sublist_at predicate: s appears at position i in t",
            "2. Define sublist predicate: exists i. sublist_at s t i",
            "3. Implement checker with nested loops/recursion",
            "4. Outer loop: try each starting position",
            "5. Inner loop: check if all elements match"
        ])

    if not result["operations"]:
        result["suggested_approach"] = [
            "1. Define clear specification as a predicate",
            "2. Write implementation that satisfies the spec",
            "3. Use refinement types to encode the specification",
            "4. Add 'decreases' clauses for recursive functions",
            "5. Add intermediate assertions to help the SMT solver"
        ]

    return result


def cmd_search_lemmas(query: str) -> list:
    """Search for lemmas matching query"""
    docs = get_docs_index()
    lemmas = docs.search_lemmas(query, limit=10)

    return [
        {
            "name": f"{l.module}.{l.name}",
            "signature": l.signature,
            "body_preview": l.body[:200] + "..." if len(l.body) > 200 else l.body
        }
        for l in lemmas
    ]


def cmd_search_examples(query: str) -> list:
    """Search for examples matching query"""
    docs = get_docs_index()
    examples = docs.search_examples(query, limit=5)

    return [
        {
            "name": e.name,
            "description": e.description,
            "file": e.source_file,
            "code_preview": e.code[:500] + "..." if len(e.code) > 500 else e.code
        }
        for e in examples
    ]


def cmd_verify(filepath: str) -> dict:
    """Verify an F* file using Docker"""
    filepath = Path(filepath)
    if not filepath.exists():
        return {"success": False, "error": f"File not found: {filepath}"}

    workspace = Path.cwd()
    docker_path = "/Applications/Docker.app/Contents/Resources/bin/docker"

    # Determine container path
    try:
        rel_path = filepath.relative_to(workspace)
        container_path = f"/workspace/{rel_path}"
    except ValueError:
        return {"success": False, "error": "File must be within workspace"}

    cmd = [
        docker_path, "run", "--rm",
        "-v", f"{workspace}:/workspace",
        "fstar-proof-agent", "fstar.exe", container_path
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            env={**os.environ, "PATH": f"/Applications/Docker.app/Contents/Resources/bin:{os.environ.get('PATH', '')}"}
        )
        output = result.stdout + result.stderr

        # Filter warnings
        output_lines = [l for l in output.split('\n') if 'WARNING' not in l]
        output = '\n'.join(output_lines).strip()

        success = "Verified module" in output or "All verification conditions discharged" in output

        return {
            "success": success,
            "output": output,
            "errors": _parse_errors(output) if not success else []
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def cmd_get_errors(filepath: str) -> list:
    """Get detailed error analysis for an F* file"""
    result = cmd_verify(filepath)
    if result.get("success"):
        return []

    errors = result.get("errors", [])

    # Enhance with suggestions
    for error in errors:
        error["suggestions"] = _suggest_fix_for_error(error)

    return errors


def cmd_suggest_fix(filepath: str) -> dict:
    """Suggest fixes for errors in an F* file"""
    errors = cmd_get_errors(filepath)
    if not errors:
        return {"status": "no_errors", "message": "File verifies successfully"}

    suggestions = []
    for error in errors:
        suggestions.append({
            "error": error["message"][:100],
            "line": error.get("line"),
            "fix": error.get("suggestions", "No automatic suggestion available")
        })

    return {
        "status": "has_errors",
        "error_count": len(errors),
        "suggestions": suggestions
    }


def _parse_errors(output: str) -> list:
    """Parse F* error messages"""
    errors = []
    pattern = r'\*\s*Error\s+(\d+)\s+at\s+[^(]+\((\d+),(\d+)[^:]*:\s*\n\s*-\s*(.+?)(?=\n\*|\n\n|$)'

    for match in re.finditer(pattern, output, re.DOTALL):
        errors.append({
            "code": match.group(1),
            "line": int(match.group(2)),
            "col": int(match.group(3)),
            "message": match.group(4).strip()
        })

    return errors


def _suggest_fix_for_error(error: dict) -> str:
    """Suggest a fix for a specific error"""
    msg = error.get("message", "")

    if "module declaration" in msg:
        return "Rename the module to match the filename, or rename the file"

    if "Identifier not found" in msg:
        match = re.search(r'\[(\w+)\]', msg)
        if match:
            ident = match.group(1)
            return f"Add 'open' for module containing '{ident}', or define '{ident}'"

    if "Expected type" in msg:
        return "Check the types match. May need to add a coercion or adjust the refinement"

    if "Could not prove" in msg:
        return "Add intermediate assertions, invoke a lemma, or strengthen preconditions"

    if "Subtyping check failed" in msg:
        return "The refinement type constraint isn't satisfied. Check preconditions or add an assertion"

    if "Duplicate" in msg:
        return "Rename one of the duplicate definitions"

    return "Review the error message and adjust the code accordingly"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "analyze":
        if not args:
            print("Usage: fstar_tools.py analyze <task>")
            sys.exit(1)
        result = cmd_analyze(" ".join(args))
        print(json.dumps(result, indent=2))

    elif cmd == "search-lemmas":
        if not args:
            print("Usage: fstar_tools.py search-lemmas <query>")
            sys.exit(1)
        result = cmd_search_lemmas(" ".join(args))
        print(json.dumps(result, indent=2))

    elif cmd == "search-examples":
        if not args:
            print("Usage: fstar_tools.py search-examples <query>")
            sys.exit(1)
        result = cmd_search_examples(" ".join(args))
        print(json.dumps(result, indent=2))

    elif cmd == "verify":
        if not args:
            print("Usage: fstar_tools.py verify <file>")
            sys.exit(1)
        result = cmd_verify(args[0])
        print(json.dumps(result, indent=2))

    elif cmd == "get-errors":
        if not args:
            print("Usage: fstar_tools.py get-errors <file>")
            sys.exit(1)
        result = cmd_get_errors(args[0])
        print(json.dumps(result, indent=2))

    elif cmd == "suggest-fix":
        if not args:
            print("Usage: fstar_tools.py suggest-fix <file>")
            sys.exit(1)
        result = cmd_suggest_fix(args[0])
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
