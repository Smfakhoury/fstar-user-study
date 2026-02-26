# Agent Improvements Over Baseline

## Baseline (Vanilla Claude)
- Direct code generation
- No structured approach
- No specification focus
- Blind iteration on errors

## Improved Agent

### 1. Task Decomposition (`lib/decompose.py`)
**Paper finding:** "Participants mitigate difficulty by decomposing a task into smaller, manageable subgoals"

```bash
python3 lib/decompose.py "binary search in sorted sequence"
# Returns: is_sorted → search_bounds → search_correct
```

**Impact:** Address complex proofs in order, each subgoal has clear spec hint.

---

### 2. Lemma RAG (`lib/fstar_rag.py`)
**Paper finding:** "Experts emphasized finding relevant lemmas before diving into the proof"

```bash
python3 lib/fstar_rag.py "sequence index"
# Returns: Seq.index, Seq.length, lemma_index_slice, etc.
```

**Impact:** Know what tools are available BEFORE writing code.

---

### 3. Smart Error Analysis (`lib/error_analysis.py`)
**Paper finding:** "Frequent and iterative reliance on the verifier"

Instead of blind iteration:
- Parse error type (termination, refinement, SMT failure, etc.)
- Suggest targeted fix strategy
- Provide code hints

**Impact:** Fix errors intelligently, not randomly.

---

### 4. Bounded Errors Strategy
**Paper finding:** "P8 intentionally maintained 0-4 active errors, achieving better outcomes"

When errors > 4:
1. Use `assume` to defer verification on parts
2. Focus on critical errors first
3. Uncomment/prove deferred parts after core works

**Impact:** Don't get overwhelmed by error avalanche.

---

### 5. Spec Refinement Loop
**Paper finding:** "Participants iteratively revisit specifications to strengthen them"

When stuck after 3 attempts:
1. Re-examine spec structure
2. Try alternate quantifier formulation (P8: "forall version worked immediately")
3. Simplify over-ambitious specs

**Impact:** Adapt spec to what's provable.

---

### 6. Multi-shot Examples
**Paper finding:** Expert patterns are predictive of success

Show working patterns before generating:
- Refinement with membership
- Spec equivalence proofs
- Lemmas for non-obvious properties

**Impact:** Prime the model with good patterns.

---

## Expected Improvement

| Metric | Baseline | Improved Agent |
|--------|----------|----------------|
| Has specs | 0% | 100% |
| Iterations (same) | ~2 | ~2 |
| Quality (specs prove correctness) | NO | YES |
| Handles complex tasks | Fails | Decomposes |
| Uses stdlib lemmas | Rarely | Systematically |
| Error recovery | Blind retry | Targeted fixes |

## Testing the Improvements

```bash
# Test decomposition
python3 lib/decompose.py "intersection of two lists no duplicates"

# Test RAG
python3 lib/fstar_rag.py "list membership filter"

# Test error analysis
echo "* Error 19: Subtyping check failed - Expected nat got int" | python3 lib/error_analysis.py
```

## Next Steps to Further Improve

1. **Fine-tune on F* proofs** - Train on verified F* code from EverCrypt, HACL*, etc.
2. **Interactive mode** - Ask user for clarification on ambiguous specs
3. **Proof search** - Try multiple approaches in parallel, pick first that verifies
4. **Learning from failures** - Remember which patterns failed for similar tasks
5. **Tighter verifier integration** - Stream verification output for faster feedback
