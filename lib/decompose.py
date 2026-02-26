#!/usr/bin/env python3
"""
Task Decomposition for F* Proofs

From paper: "Participants mitigate [difficulty] by decomposing a task into
smaller, manageable subgoals, each with a well-defined purpose."

Example: P1 broke T3 (intersection) into:
1. Deduplication subgoal
2. Intersection subgoal
"""

import re
from typing import List, Dict

def decompose_task(task: str) -> List[Dict]:
    """
    Decompose a proof task into subgoals.

    Returns list of subgoals, each with:
    - name: short identifier
    - description: what to prove
    - dependencies: which subgoals must be done first
    - spec_hint: how to specify this subgoal
    """
    task_lower = task.lower()
    subgoals = []

    # Pattern: Binary search
    if "binary" in task_lower and "search" in task_lower:
        subgoals = [
            {
                "name": "is_sorted",
                "description": "Define sorted predicate for input",
                "dependencies": [],
                "spec_hint": "forall i j. i <= j ==> index s i <= index s j"
            },
            {
                "name": "search_bounds",
                "description": "Prove search maintains valid bounds",
                "dependencies": ["is_sorted"],
                "spec_hint": "lo <= mid < hi at each step"
            },
            {
                "name": "search_correct",
                "description": "Prove result is correct index or -1",
                "dependencies": ["search_bounds"],
                "spec_hint": "r >= 0 ==> index s r == target"
            }
        ]

    # Pattern: Sublist/subsequence
    elif any(w in task_lower for w in ["sublist", "subsequence", "contiguous"]):
        subgoals = [
            {
                "name": "subseq_at",
                "description": "Define 'appears at position i' predicate",
                "dependencies": [],
                "spec_hint": "forall j. j < len s ==> index s j == index t (i+j)"
            },
            {
                "name": "is_subseq",
                "description": "Define 'is subsequence' as exists position",
                "dependencies": ["subseq_at"],
                "spec_hint": "exists i. subseq_at s t i"
            },
            {
                "name": "check_single_pos",
                "description": "Check if s matches at specific position",
                "dependencies": ["subseq_at"],
                "spec_hint": "b <==> subseq_at s t pos"
            },
            {
                "name": "check_all_pos",
                "description": "Try all positions, prove equivalence to spec",
                "dependencies": ["check_single_pos", "is_subseq"],
                "spec_hint": "b <==> is_subseq s t"
            }
        ]

    # Pattern: Intersection
    elif "intersection" in task_lower:
        subgoals = [
            {
                "name": "in_both",
                "description": "Define 'element in both lists' predicate",
                "dependencies": [],
                "spec_hint": "mem x a /\\ mem x b"
            },
            {
                "name": "no_duplicates",
                "description": "Define duplicate-free property if needed",
                "dependencies": [],
                "spec_hint": "forall i j. i <> j ==> index l i <> index l j"
            },
            {
                "name": "filter_correct",
                "description": "Prove filter produces correct elements",
                "dependencies": ["in_both"],
                "spec_hint": "mem x result <==> in_both x a b"
            }
        ]

    # Pattern: Max/min difference
    elif any(w in task_lower for w in ["max", "largest"]) and any(w in task_lower for w in ["min", "smallest", "diff"]):
        subgoals = [
            {
                "name": "is_max",
                "description": "Define maximum predicate",
                "dependencies": [],
                "spec_hint": "mem x l /\\ forall y. mem y l ==> y <= x"
            },
            {
                "name": "is_min",
                "description": "Define minimum predicate",
                "dependencies": [],
                "spec_hint": "mem x l /\\ forall y. mem y l ==> y >= x"
            },
            {
                "name": "max_geq_min",
                "description": "Prove max >= min (key lemma)",
                "dependencies": ["is_max", "is_min"],
                "spec_hint": "Lemma (max_list l >= min_list l)"
            },
            {
                "name": "diff_nonneg",
                "description": "Prove difference is non-negative",
                "dependencies": ["max_geq_min"],
                "spec_hint": "r: int{r >= 0}"
            }
        ]

    # Generic decomposition
    else:
        subgoals = [
            {
                "name": "spec_predicate",
                "description": "Define what 'correct' means as a predicate",
                "dependencies": [],
                "spec_hint": "let correct (input) (output) : prop = ..."
            },
            {
                "name": "helper_lemmas",
                "description": "Identify and prove any helper lemmas needed",
                "dependencies": ["spec_predicate"],
                "spec_hint": "Lemma (ensures <property>)"
            },
            {
                "name": "implementation",
                "description": "Implement with refinement type matching spec",
                "dependencies": ["spec_predicate"],
                "spec_hint": "let solve (input) : output:_{correct input output} = ..."
            }
        ]

    return subgoals


def format_decomposition(task: str) -> str:
    """Format decomposition for display."""
    subgoals = decompose_task(task)

    lines = [f"TASK DECOMPOSITION: {task}", "=" * 50, ""]

    for i, sg in enumerate(subgoals, 1):
        deps = ", ".join(sg["dependencies"]) if sg["dependencies"] else "none"
        lines.extend([
            f"Subgoal {i}: {sg['name']}",
            f"  Description: {sg['description']}",
            f"  Dependencies: {deps}",
            f"  Spec hint: {sg['spec_hint']}",
            ""
        ])

    lines.append("ORDER: " + " → ".join(sg["name"] for sg in subgoals))
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python decompose.py <task>")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    print(format_decomposition(task))
