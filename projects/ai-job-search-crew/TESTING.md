# Public GitHub package verification — 2026-10-02

17 tests passed with fictional public seed data. One HTTP/socket test could not run because the execution environment disallows socket creation. One optional CrewAI integration test was skipped because its dependency is not installed. Real Ollama/model execution on the user's Mac remains pending.

## Earlier private-package verification

# Verification record

Build: local v1, September 2026.

## Passed

- Python 3.12 syntax and JavaScript syntax checks.
- 18 dependency-free workflow tests. The optional CrewAI test is skipped in the base environment.
- The additional integration test passed separately with **CrewAI 1.15.23** installed: all three agents used the explicit adapter and produced three simulated model calls. No paid model was used.
- A simulated Ollama transport exercised writer/reviewer generation, JSON assembly and token accounting.
- Browser interaction test in headless Chromium: open the seeded role, create drafts, edit and save a letter, complete review, record a test submission, practice an answer, and add another job. No JavaScript page errors were observed.
- Desktop screenshots inspected for layout. A 390px mobile viewport was checked for horizontal overflow.
- Excluded pressure-sore activities do not enter the draft evidence pool.
- Unknown/excluded evidence IDs and unfinished-project claims are flagged.
- Review is required before recording a first submission. Edits invalidate approval.
- Draft history and the first submission snapshot are preserved.
- Generation failures and concurrent edits retain the user's existing work.
- Cloud/remote model rejection, HTML escaping and cross-origin write rejection were tested.

Browser tests used a temporary test database. No test applications or test notes are included in the delivered project. No application was submitted to an employer.

## Not yet verified

- Real Ollama model inference and writing quality on the user's Mac. There is no downloaded model in this delivery.
- Mac-specific installation, browser print output and performance on the user's hardware.
- Semantic factual accuracy of arbitrary AI or user-written drafts. Rules and source IDs do not establish truth; human review remains necessary.

## Reproduce

From the project folder:

```bash
python3 -m unittest discover -s tests -v
```

After installing `requirements-local-ai.txt`, the same command includes the CrewAI orchestration test. It still uses simulated responses and makes no model request.

For a browser check, launch `python3 app.py`, then follow the first-application steps in `README.md`. Use a disposable database when testing submission states:

```bash
python3 app.py --database /tmp/job-search-test.sqlite3
```

Do not label simulated local-model tests as real model-quality evaluation in a portfolio description.
