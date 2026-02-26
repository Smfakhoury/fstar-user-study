# F* Proof Agent

This project provides an autonomous proof agent implementing the **spec-first planner** strategy from the ICSE user study on expert proof-writing.

## Quick Start

**Primary skill** - autonomous proof completion:
```
/fstar-prove <task description>
```

This skill handles the full workflow: representation choice → specification → implementation → verification → refinement.

**Individual commands** (for manual control):
- `/fstar-repr <task>` - Choose representation (List vs Seq, quantifiers)
- `/fstar-analyze <task>` - Analyze task and suggest approach
- `/fstar-verify <file>` - Verify an F* file using Docker
- `/fstar-search <query>` - Search for relevant lemmas and examples

## Architecture

```
Local Claude Code (AI reasoning)
         │
         ▼
Python Tools (fstar_tools.py)
         │
         ▼
Docker Container (F* verifier)
```

## Proof Strategy (from ICSE User Study)

Follow the **spec-first planner** approach:

### Step 0: Choose Representation (CRITICAL)
> "Experts deliberated on the most suitable representation, balancing efficiency
> with proof complexity—e.g., choosing between Seq and List"

Use `/fstar-repr` to decide:
- **List vs Seq**: Seq for indexing, List for membership/recursion
- **Quantifiers**: Index-based forall vs element-based, avoid exists in return types
- **Spec structure**: Align with how you'll iterate in implementation

### Steps 1-5: Implement
1. **Analyze** - Understand the task, identify operations
2. **Specify** - Write specifications first (predicates, pre/postconditions)
3. **Implement** - Write implementation that satisfies the spec
4. **Verify** - Run F* verifier, interpret errors
5. **Refine** - Fix errors iteratively, keeping active errors bounded (≤4)

## Key Files

- `fstar_tools.py` - CLI tools for analysis, verification, search
- `ground-truth/` - Example solutions from the user study
- `examples/stdlib/` - F* standard library excerpts
- `output/` - Generated proof files

## F* Patterns

### Refinement Types
```fstar
val f: x:int{x > 0} -> y:int{y > x}
```

### Specifications as Predicates
```fstar
let is_sorted (xs: list int) : prop =
    forall (i j: nat). i <= j /\ j < length xs ==> index xs i <= index xs j
```

### Recursive Functions with Termination
```fstar
val factorial: n:nat -> Tot nat (decreases n)
let rec factorial n = if n = 0 then 1 else n * factorial (n - 1)
```

### Lemmas
```fstar
val my_lemma: x:int -> Lemma (requires x > 0) (ensures x + 1 > 1)
let my_lemma x = ()
```

## Common Modules

- `FStar.List.Tot` - List operations (length, index, mem, contains, filter)
- `FStar.List.Tot.Properties` - List lemmas
- `FStar.Seq` - Sequences (arrays)
- `FStar.Seq.Properties` - Sequence lemmas
