# /fstar-search

Search for relevant F* lemmas and examples.

## Usage
```
/fstar-search <query>
```

## What it does

1. Searches indexed F* standard library for matching lemmas
2. Searches ground-truth examples for relevant code
3. Returns signatures and code snippets

## Instructions

When this command is invoked, run both:

```bash
cd /Users/sarahfakhoury/fstar-proof-agent && python3 fstar_tools.py search-lemmas "$ARGUMENTS"
```

```bash
cd /Users/sarahfakhoury/fstar-proof-agent && python3 fstar_tools.py search-examples "$ARGUMENTS"
```

Present the results showing:
1. Relevant lemmas with their signatures
2. Relevant examples with code snippets
3. Suggestions for how to use them

## Example

```
/fstar-search intersection contains filter
```

Returns lemmas like `mem_filter`, `contains_cons`, and example code from Task249.
