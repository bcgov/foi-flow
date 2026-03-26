# FOIMOD Delete Mode Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a request-based delete mode that previews affected FOIMOD rows by default and only performs deletes when `--confirm-delete` is present.

**Architecture:** Extend the existing CLI with a delete branch that uses the current request-processing loop. Add FOIDB client methods for resolving related ids, preview counts, and deleting in FK-safe order, then add an execution path that returns per-request results compatible with the existing CSV output.

**Tech Stack:** Python, argparse, SQL, pytest

---

## Chunk 1: CLI and Request Flow

### Task 1: Add failing CLI tests for delete mode

**Files:**
- Modify: `tests/test_migrator.py`
- Modify: `src/main.py`

- [ ] **Step 1: Write the failing test**

Add tests that expect `run()` to call delete behavior when `--delete` is set and to preserve preview-only behavior without `--confirm-delete`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_migrator.py -v`
Expected: FAIL because delete mode is not implemented

- [ ] **Step 3: Write minimal implementation**

Update the parser and request loop to support delete mode flags and route request ids to delete behavior.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_migrator.py -v`
Expected: PASS

### Task 2: Add a request-level delete workflow

**Files:**
- Modify: `src/migrator.py`
- Modify: `tests/test_migrator.py`

- [ ] **Step 1: Write the failing test**

Add tests for preview results, confirmed delete results, not-found handling, and rollback on delete failure.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_migrator.py -v`
Expected: FAIL because delete workflow is missing

- [ ] **Step 3: Write minimal implementation**

Add a request-level delete method that begins a transaction, resolves linked ids, previews counts, conditionally deletes, and returns result rows.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_migrator.py -v`
Expected: PASS

## Chunk 2: FOIDB Preview and Delete Operations

### Task 3: Add failing FOIDB client tests for request resolution and delete execution

**Files:**
- Modify: `tests/test_foidb_client.py`
- Modify: `src/foidb_client.py`

- [ ] **Step 1: Write the failing test**

Add tests for:
- resolving a request bundle by `migrationreference`
- previewing per-table delete counts
- deleting rows in the expected table order

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_foidb_client.py -v`
Expected: FAIL because the FOIDB client methods do not exist

- [ ] **Step 3: Write minimal implementation**

Add resolution, preview, and delete methods using parameterized SQL and the current transaction wrapper.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_foidb_client.py -v`
Expected: PASS

## Chunk 3: Documentation and End-to-End Verification

### Task 4: Update README for delete mode

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write the failing documentation expectation**

Identify the CLI, flow, and usage sections that need delete-mode coverage.

- [ ] **Step 2: Update the README**

Document the new flags, preview behavior, confirmed delete behavior, and example usage.

- [ ] **Step 3: Verify the README content**

Review the changed sections for consistency with the implemented behavior.

### Task 5: Run full verification

**Files:**
- Modify: `tests/test_foidb_client.py`
- Modify: `tests/test_migrator.py`
- Modify: `README.md`

- [ ] **Step 1: Run focused tests**

Run: `pytest tests/test_foidb_client.py tests/test_migrator.py -v`
Expected: PASS

- [ ] **Step 2: Run full suite**

Run: `pytest`
Expected: PASS
