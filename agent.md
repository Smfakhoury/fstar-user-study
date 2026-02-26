# F* Proof Agent

An AI-powered proof assistant for F* that embodies the **spec-first planner** strategy identified in the ICSE user study of expert proof-writing processes.

## Core Strategy

This agent implements the three key characteristics of effective proof engineering:

1. **Deliberate Early Specification Drafting** - Front-load specification effort before diving into implementation
2. **Measured Verifier Invocation** - Avoid tight edit-verify loops; think before invoking
3. **Disciplined Error Management** - Keep active errors bounded; frequently return to clean state

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PROOF EXPERT AGENT                         │
│  - Understands proof strategy and high-level reasoning          │
│  - Decomposes tasks into subgoals                               │
│  - Generates proof sketches with specs, lemmas, structure       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     F* SYNTAX EXPERT AGENT                       │
│  - Translates sketches to valid F* syntax                       │
│  - Fixes type errors and syntax issues                          │
│  - Has access to F* documentation and libraries                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        F* VERIFIER                               │
│  - Runs fstar.exe on generated code                             │
│  - Returns verification errors or success                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     [Feedback Loop]
```

## Workflow

### Phase 1: Planning (Spec-First)
1. Parse the task description and test cases
2. Identify required pre/postconditions
3. Determine appropriate data structures (List vs Seq, etc.)
4. Plan decomposition into helper functions/lemmas
5. Generate a proof sketch with `assume` placeholders

### Phase 2: Iterative Refinement
1. Translate sketch to F* code
2. Verify with bounded error tolerance (max 4 active errors)
3. If errors exceed threshold: comment out failing sections
4. Address one subgoal at a time
5. Remove `assume`/`admit` incrementally

### Phase 3: Validation
1. Ensure all `assume`/`admit` removed
2. Run full verification
3. Check test cases pass

## Key Behaviors (from paper findings)

- **Task Decomposition**: Break complex proofs into subgoals with clear purposes
- **Spec-Impl Alignment**: Structure specifications to match implementation iteration
- **Library Reuse**: Leverage existing lemmas from FStar.List.Tot, FStar.Seq, etc.
- **Defer Mechanism**: Use `assume`/`admit` to defer subgoals, not accumulate errors
- **Think Pauses**: Before each verifier call, reason about expected outcome

## Skills

| Skill | Purpose |
|-------|---------|
| `/sketch-proof` | Generate high-level proof sketch with specs and structure |
| `/fix-syntax` | Fix F* syntax errors using documentation |
| `/verify` | Run F* verifier and interpret results |
| `/lookup-lemma` | Search for relevant lemmas in F* libraries |
| `/decompose` | Break task into smaller subgoals |

## Configuration

```yaml
max_active_errors: 4
max_refinement_loops: 15
defer_on_stuck: true
think_before_verify: true
early_spec_ratio: 0.7  # 70% of Q1 edits should be spec
```

## Usage

```bash
# Start the agent
python agent.py --task "Implement binary search with verification"

# Or use skills directly
/sketch-proof "Returns intersection of two arrays without duplicates"
/verify code.fst
/lookup-lemma "list membership"
```
