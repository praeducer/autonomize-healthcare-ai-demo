# Reliable PPTX Generation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the broken pptxgenjs pipeline with a self-contained Python script that generates a clean PPTX every time — no repair dialogs, no external repo dependencies.

**Architecture:** `scripts/generate_deck.py` uses python-pptx to produce the PPTX. DOCX generation stays unchanged (deck-builder works fine). `make deck` runs diagrams, then the Python PPTX script, then the TypeScript DOCX script.

**Tech Stack:** python-pptx, Python 3.12+

**Why:** pptxgenjs 4.0.1 generates OOXML-violating files (phantom Content_Types entries, possibly more). Post-processing can't reliably fix all issues. python-pptx is the industry standard and produces clean files natively.

**Scope:** PPTX generation only. Do not touch DOCX pipeline.

---

### Task 1: Add python-pptx dependency

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add to dependencies**

```toml
"python-pptx>=1.0.0",
```

**Step 2: Install**

Run: `pip install -e ".[dev]"`

**Step 3: Verify**

Run: `python -c "from pptx import Presentation; print('OK')"`

**Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "deps: add python-pptx for PPTX generation"
```

---

### Task 2: Write `scripts/generate_deck.py`

**Files:**
- Create: `scripts/generate_deck.py`

The script:
1. Defines the Autonomize brand theme (same colors/fonts as generate-deck.ts)
2. Defines all 14 slides inline (same content as generate-deck.ts)
3. Renders PPTX with python-pptx:
   - 13.33" x 7.5" widescreen layout
   - Title bar: 0.9" purple rect + white text
   - Blocks: text, heading, image (with maxH cap), callout, table
   - Slide numbers in footer
4. Saves with timestamped filename to `docs/presentation/`

**Step 1: Write the script**

Port the slide data from `generate-deck.ts` to Python. Use python-pptx APIs for layout.

**Step 2: Run**

Run: `python scripts/generate_deck.py`

**Step 3: Open in PowerPoint — MUST open without repair dialog**

This is the only acceptance criterion that matters.

**Step 4: Commit**

```bash
git add scripts/generate_deck.py
git commit -m "feat: python-pptx PPTX generator — no repair dialog"
```

---

### Task 3: Update Makefile

**Files:**
- Modify: `Makefile`

**Step 1: Update `deck` target**

```makefile
deck: diagrams
	python scripts/generate_deck.py
	npx tsx scripts/generate-deck.ts
```

Python generates PPTX. TypeScript generates DOCX (unchanged).

**Step 2: Remove PPTX generation from generate-deck.ts**

Remove the `renderPptx` call. Keep only `renderDocx`. Remove the import of `renderPptx`.

**Step 3: Verify both run**

**Step 4: Commit**

```bash
git add Makefile scripts/generate-deck.ts
git commit -m "refactor: PPTX via python-pptx, DOCX via deck-builder"
```

---

### Task 4: Visual QA

For all 14 slides verify:
- Title fits, no clipping
- Text within margins
- Tables: all columns visible
- Images: proportional, centered
- Slide numbers in footer

Fix issues, re-run, re-verify until clean.

---

### Task 5: Cleanup

- Remove stale PPTX files from `docs/presentation/`
- Update `docs/ai-tooling.md` and `docs/README.md` references
- Final commit
