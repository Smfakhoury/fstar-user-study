# /fstar-prove

Autonomous F* proof agent implementing the **spec-first planner** strategy.

## Usage
```
/fstar-prove <task description>
```

## Agent Strategy (Grounded in ICSE Paper Findings)

### Phase 0: DECOMPOSITION (NEW)
> "Participants mitigate difficulty by decomposing a task into smaller, manageable subgoals"

Run: `python3 lib/decompose.py "$ARGUMENTS"`

This breaks the task into ordered subgoals. Address them in dependency order.

### Phase 1: REPRESENTATION CHOICE
> "Experts deliberated on the most suitable representation"

Run: `python3 fstar_tools.py analyze "$ARGUMENTS"`

Choose:
- **Seq** for indexing, slicing, position-based proofs
- **List** for membership, filtering, recursive folds
- **Quantifier style**: index-based forall vs element-based

### Phase 2: LEMMA LOOKUP (NEW - RAG)
> "Experts emphasized finding relevant lemmas before diving into the proof"

Run: `python3 lib/fstar_rag.py "<relevant keywords>"`

Get relevant stdlib functions and lemmas BEFORE writing code.

### Phase 3: SPEC-FIRST WRITING
> "70% of Q1 effort is on specification"

For EACH subgoal from decomposition:
1. Write spec predicate FIRST
2. Then write implementation satisfying that spec
3. Verify incrementally

Template:
```fstar
(* SUBGOAL: <name> *)
(* SPEC *)
let <spec_predicate> ... : prop = ...

(* IMPL *)
let <function> ... : result:_{<spec_predicate> ...} = ...
```

### Phase 4: BOUNDED ERROR VERIFICATION (NEW)
> "Successful users kept ≤4 active errors"

After each verify:
1. Run: `python3 lib/error_analysis.py` on errors
2. If errors > 4: Use `assume`/`admit` to defer parts
3. Fix errors in priority order:
   - Termination (add decreases)
   - Incomplete patterns (add preconditions)
   - Undefined (add opens)
   - Refinement (add assertions/lemmas)

### Phase 5: SPEC REFINEMENT LOOP (NEW)
> "Participants iteratively revisit specifications to strengthen them"

If stuck after 3 attempts on same error:
1. Re-examine the specification
2. Consider if spec structure matches implementation
3. Try alternate quantifier formulation
4. Simplify spec if overly ambitious

## Error-Driven Fix Strategies

| Error Type | Fix Strategy |
|------------|--------------|
| `Subtyping (nat/int)` | Add bounds check `if x >= 0` |
| `Subtyping (index)` | Prove `i < length` before indexing |
| `Termination` | Add `(decreases measure)` clause |
| `Incomplete patterns` | Add precondition or handle empty case |
| `SMT failure` | Add intermediate `assert` statements |
| `Undefined` | Add `open FStar.List.Tot` etc. |

## Multi-Shot Examples (Show Before Generating)

Before writing code, recall these expert patterns:

**Pattern: Refinement with membership**
```fstar
let rec max_list (l: list int{length l > 0})
    : Tot (r: int{mem r l /\ (forall y. mem y l ==> y <= r)}) =
    match l with
    | [x] -> x
    | hd :: tl -> let m = max_list tl in if hd >= m then hd else m
```

**Pattern: Spec equivalence**
```fstar
let check (s t: seq a)
    : b: bool{b <==> is_subseq s t} =  // Prove equivalence to spec
```

**Pattern: Lemma for non-obvious property**
```fstar
let max_geq_min (l: list int{length l > 0})
    : Lemma (max_list l >= min_list l) = ()  // May need induction
```

## Success Criteria

1. ✓ All subgoals verified
2. ✓ Main function has spec matching task requirements
3. ✓ No `admit()` or `assume` in final code
4. ✓ Tests pass (add `let test: squash (...) = ()`)

## Iteration Limits

- Max 10 verification iterations total
- Max 3 iterations on same error before trying alternate approach
- If stuck: Ask for help with specific error

## Commands Used

```bash
# Decomposition
python3 lib/decompose.py "task description"

# Representation choice
python3 fstar_tools.py analyze "task description"

# Lemma lookup
python3 lib/fstar_rag.py "keywords"

# Verification
python3 fstar_tools.py verify output/File.fst

# Error analysis
python3 lib/error_analysis.py  # (reads from stdin or file)
```
