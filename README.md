# F* Proof Agent

An LLM-powered proof agent for F* that implements the **spec-first planner** strategy from the ICSE user study on expert proof-writing.

## Quick Start

### 1. Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)

### 2. Build the F* Docker Image

```bash
docker build -t fstar-proof-agent .
```

### 3. Run the Agent

Open Claude Code in this directory:

```bash
claude
```

Then use the proof skill:

```
/fstar-prove <task description>
```

Example:
```
/fstar-prove Find the maximum element in a non-empty list and prove it's >= all elements
```

## Agent Commands

| Command | Description |
|---------|-------------|
| `/fstar-prove <task>` | **Main skill** - autonomous proof completion |
| `/fstar-repr <task>` | Choose representation (List vs Seq) |
| `/fstar-analyze <task>` | Analyze task, suggest approach |
| `/fstar-verify <file>` | Verify an F* file |
| `/fstar-search <query>` | Search for lemmas |

## How It Works

The agent follows expert strategies from the ICSE user study:

```
┌─────────────────────────────────────────────────────────────┐
│  1. DECOMPOSE     Break task into ordered subgoals         │
│  2. REPR CHOICE   Choose List vs Seq, quantifier style     │
│  3. LEMMA LOOKUP  Search stdlib for relevant functions     │
│  4. SPEC FIRST    Write specifications before impl (70%)   │
│  5. VERIFY LOOP   Iterate with bounded errors (≤4)         │
│  6. REFINE        Adjust specs when stuck                  │
└─────────────────────────────────────────────────────────────┘
```

## Manual Usage (Without Claude Code)

### Verify a file directly:

```bash
docker run --rm -v "$(pwd):/workspace" fstar-proof-agent \
    fstar.exe /workspace/your_file.fst
```

### Use the Python tools:

```bash
# Analyze a task
python3 fstar_tools.py analyze "binary search in sorted array"

# Decompose into subgoals
python3 lib/decompose.py "intersection of two lists"

# Search for lemmas
python3 lib/fstar_rag.py "sequence index length"

# Verify a file
python3 fstar_tools.py verify output/MyProof.fst
```

## Project Structure

```
fstar-proof-agent/
├── Dockerfile                 # F* verification environment
├── CLAUDE.md                  # Agent instructions
├── fstar_tools.py             # CLI tools for verification
├── lib/
│   ├── decompose.py           # Task decomposition
│   ├── fstar_rag.py           # Lemma search (RAG)
│   └── error_analysis.py      # Smart error fixing
├── .claude/
│   ├── skills/
│   │   └── fstar-prove.md     # Main autonomous skill
│   └── commands/
│       ├── fstar-repr.md      # Representation choice
│       ├── fstar-analyze.md   # Task analysis
│       ├── fstar-verify.md    # Verification
│       └── fstar-search.md    # Lemma search
├── benchmark/                 # Benchmark results
│   ├── improved/              # Agent with specs
│   └── vanilla_v2/            # Baseline without specs
└── output/                    # Generated proofs
```

## Key Findings from User Study

1. **Spec-first wins**: Experts spend 70% of early time on specifications
2. **Representation matters**: Seq for indexing, List for membership
3. **Bounded errors**: Keep ≤4 active errors at a time
4. **Decomposition**: Break complex proofs into subgoals

## Extending the Agent

### Add new proof patterns:

Edit `lib/fstar_rag.py` to add common lemmas:

```python
FStarDefinition("my_lemma", "MyModule", "lemma",
    "val my_lemma: ... -> Lemma (...)",
    "Description of what it proves", "", 0),
```

### Add task decomposition patterns:

Edit `lib/decompose.py` to add new task types:

```python
elif "my_pattern" in task_lower:
    subgoals = [
        {"name": "step1", "description": "...", ...},
        ...
    ]
```

## Citation

Based on findings from:

> ["What's in a Proof? Analyzing Expert Proof-Writing Processes in F* and Verus"](https://arxiv.org/pdf/2508.02733)


## License

MIT


