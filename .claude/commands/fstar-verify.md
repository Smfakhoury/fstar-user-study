# /fstar-verify

Verify an F* file using the Docker-containerized F* verifier.

## Usage
```
/fstar-verify <file.fst>
```

## What it does

1. Runs F* verifier in Docker container
2. Parses verification output
3. Reports success or detailed errors with fix suggestions

## Instructions

When this command is invoked, run:

```bash
cd /Users/sarahfakhoury/fstar-proof-agent && PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" docker run --rm -v "$(pwd):/workspace" fstar-proof-agent fstar.exe "/workspace/$ARGUMENTS" 2>&1 | grep -v WARNING
```

Then interpret the output:
- If "Verified module" appears → SUCCESS
- Otherwise, parse errors and suggest fixes based on error type:
  - **Module mismatch**: Rename module to match filename
  - **Identifier not found**: Add appropriate `open` statement
  - **Type error**: Check refinement types match
  - **Could not prove**: Add intermediate assertions or invoke lemmas

## Example

```
/fstar-verify output/MyProof.fst
```
