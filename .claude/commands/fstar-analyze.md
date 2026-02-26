# /fstar-analyze

Analyze an F* proof task and suggest an approach.

## Usage
```
/fstar-analyze <task description>
```

## What it does

1. Runs `python3 fstar_tools.py analyze "<task>"` to get structured analysis
2. Returns:
   - Identified data structures (list, seq, etc.)
   - Required operations (search, filter, etc.)
   - Step-by-step suggested approach
   - Relevant F* modules to use
   - Complexity notes

## Instructions

When this command is invoked, run:

```bash
cd /Users/sarahfakhoury/fstar-proof-agent && python3 fstar_tools.py analyze "$ARGUMENTS"
```

Then interpret the JSON output and explain:
1. What data structures are involved
2. What the suggested approach is
3. Which modules to import
4. Any complexity considerations

## Example

```
/fstar-analyze Write a function to find the intersection of two arrays
```

Output explains:
- Use `list` data structure
- Spec: `forall x. contains x result <==> contains x a /\ contains x b`
- Import `FStar.List.Tot`
- Use recursive implementation with `contains`
