# /fstar-repr

Choose the best data representation for a proof task.

## Why This Matters

From the ICSE user study on expert proof-writing:

> "Experts deliberated on the most suitable representation for the implementation,
> balancing efficiency with proof complexity—e.g., choosing between Seq and List"

> "Decisions on quantifiers also influenced task difficulty. P8 noted: 'I spent most
> of the time on what seemed like a simple property of subranges but eventually
> decided to rewrite the invariant directly using forall, not subranges, and the
> forall version worked immediately.'"

**This is Step 0 before writing any code.**

## Usage
```
/fstar-repr <task description>
```

## What it analyzes

1. **Data structure choice**: List vs Seq vs custom type
2. **Quantifier choice**: forall vs exists, indices vs elements
3. **Spec structure**: How to align spec with implementation

## Decision Matrix

| Need | Prefer Seq | Prefer List |
|------|-----------|-------------|
| Random access (index i) | ✓ O(1) | O(n) |
| Slicing (subrange) | ✓ built-in | manual |
| Pattern matching | awkward | ✓ natural |
| Membership test | quantify indices | ✓ built-in mem |
| Recursive processing | convert to list | ✓ natural |
| Length-indexed proofs | ✓ length is pure | length is pure |

## Quantifier Guidelines

| Pattern | Recommendation |
|---------|----------------|
| "all elements satisfy P" | `forall x. mem x l ==> P x` or `forall i. i < length ==> P (index i)` |
| "some element satisfies P" | Return the element/index explicitly, avoid `exists` in return type |
| "sorted" | Index-based: `forall i j. i < j ==> ...` |
| "no duplicates" | `forall i j. i <> j ==> index i <> index j` |

## Instructions

When this command is invoked:

1. Run: `python3 fstar_tools.py analyze "$ARGUMENTS"`
2. Focus on the `representation_choice` field
3. Explain the tradeoffs for this specific task
4. Make a clear recommendation with justification
5. Show how the spec would look with each choice

## Example

```
/fstar-repr Check if a list contains a contiguous sublist
```

Output:
```
REPRESENTATION DECISION
=======================

Recommendation: Seq

Reasoning:
- Task requires checking positions ("contiguous" = at some index i)
- Need to compare elements at specific indices
- Slicing/subrange operations natural with Seq

Tradeoffs:
- Seq: Clean index-based spec, O(1) access
- List: Would need index function (O(n)), messier proofs

Spec with Seq:
  let is_subseq_at s t i =
    forall j. j < length s ==> index s j == index t (i + j)

Spec with List (worse):
  let is_sublist_at s t i =
    forall j. j < length s ==> index s j == index t (i + j)  // O(n) index!

Quantifier choice:
- Use index-based forall (cleaner than element-based for position proofs)
- Avoid exists in return type; return bool with refinement instead
```
