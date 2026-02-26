# /fstar-new

Start a new F* proof task with full scaffolding.

## Usage
```
/fstar-new <task description>
```

## What it does

1. Analyzes the task to understand requirements
2. Searches for relevant examples and lemmas
3. Creates a new .fst file with:
   - Module declaration
   - Appropriate imports
   - Specification predicates
   - Implementation skeleton
   - Test cases
4. Verifies the initial skeleton

## Instructions

When this command is invoked:

### Step 1: Analyze
```bash
cd /Users/sarahfakhoury/fstar-proof-agent && python3 fstar_tools.py analyze "$ARGUMENTS"
```

### Step 2: Search for examples
```bash
cd /Users/sarahfakhoury/fstar-proof-agent && python3 fstar_tools.py search-examples "$ARGUMENTS"
```

### Step 3: Create the proof file

Based on the analysis:
1. Create a new file in `output/` with appropriate module name
2. Add imports based on suggested_modules
3. Write specification predicates following suggested_approach
4. Add implementation skeleton (can use `admit()` initially)
5. Add test cases

### Step 4: Verify
Run `/fstar-verify` on the new file

### Step 5: Iterate
If verification fails, interpret errors and fix them

## Example

```
/fstar-new Write a function that returns the maximum element of a non-empty list
```

Creates `output/MaxElement.fst` with:
- `is_max` predicate specification
- Recursive `max_element` function
- Refinement type ensuring result is the maximum
- Test cases
