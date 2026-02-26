# /fstar-fix

Analyze and fix errors in an F* file.

## Usage
```
/fstar-fix <file.fst>
```

## What it does

1. Runs verification to get current errors
2. Analyzes each error type
3. Suggests and applies fixes
4. Re-verifies until success or max iterations

## Instructions

When this command is invoked:

### Step 1: Get errors
```bash
cd /Users/sarahfakhoury/fstar-proof-agent && python3 fstar_tools.py suggest-fix "$ARGUMENTS"
```

### Step 2: Read the file
Use the Read tool to see the current code

### Step 3: Apply fixes based on error type

**Module name mismatch:**
- Edit the `module` declaration to match filename

**Identifier not found [X]:**
- Search for X in lemma index
- Add appropriate `open` statement
- Or define the missing identifier

**Expected type X, got type Y:**
- Check the refinement types
- May need to add coercion or adjust type annotation
- Check if preconditions are sufficient

**Could not prove P:**
- Add `assert P` before the failing line to help SMT
- Search for a lemma about P
- Invoke the lemma before the failing expression
- Consider strengthening preconditions

**Subtyping check failed:**
- The refinement isn't satisfied
- Add intermediate assertions
- May need a lemma to establish the property

### Step 4: Re-verify
After each fix, run `/fstar-verify` to check progress

### Step 5: Iterate
Continue until verified or stuck (then ask user for guidance)

## Error Limit

Following the spec-first planner strategy, if there are more than 4 active errors:
1. Comment out failing sections with `(* TODO: ... *)`
2. Add `admit()` placeholders
3. Focus on one section at a time
4. Incrementally remove admits
