# AI Job Search Crew

I am developing a local workspace for biomedical-engineering job applications: pasted posting → evidence matching → editable drafts → human review → application tracking.

## Implemented

- Python dashboard with SQLite persistence and editable application drafts.
- Source-linked candidate evidence, requirement matching, and explicit eligibility questions.
- Review checklist, draft history, company notes, and manual submission tracking.
- Optional local Ollama and three-agent CrewAI integration; no paid API requirement.

## Run

```sh
python3 app.py
# Open http://127.0.0.1:8765
python3 -m unittest discover -s tests -v
```

Python 3.10+ is required. The default workflow uses the standard library. Optional local AI dependencies are in requirements-local-ai.txt. A locally installed Ollama model is required for AI generation. Real local-model testing on my Mac remains pending.

## Scope and status

This is an ongoing personal training project. It does not discover live jobs, submit applications, or send messages. The included Arthrex posting is a historical test case, not a verified current vacancy. Human review remains required.

The public seed uses a fictional candidate profile and placeholder contact information. Prior tests in TESTING.md used the original private fixture; the public demo fixture differs. Replace the seed with your own profile before personal use. Working data is stored locally in data/private and must remain out of Git.

## Author and context

**Project owner:** Hritika Adhikary  
**Context:** Personal AI-agent training project, September–October 2026.  
**Implementation:** Developed with AI coding assistance; validation details are in TESTING.md.

## Rights

My original project material is all rights reserved. Dependencies retain their respective licenses.
