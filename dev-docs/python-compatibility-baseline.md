# Python Compatibility Baseline

Recorded 2026-05-30 for Phase 1, Session 3. This is developer-only compatibility evidence, not public support documentation.

## Current Python Facts

- Official Python sources list Python 3.14.5 as the latest Python 3 release, released 2026-05-10: https://www.python.org/downloads/latest/ and https://www.python.org/downloads/source/.
- Local default `python --version` and `python3 --version` both reported `Python 3.14.5`.
- Repo-local `venv/bin/python --version` reported `Python 3.13.13`.
- Package metadata remains `python_requires=">=3.10"` with classifiers through Python 3.13.

## Python 3.14 Resolution Evidence

Session 3 used `/tmp/agentforge-py314-compat` so the repo-local Python 3.13 venv was not replaced.

| Surface | Command | Result |
| --- | --- | --- |
| Runtime/package metadata | `/tmp/agentforge-py314-compat/bin/python -m pip install --dry-run --report /tmp/agentforge-py314-setup-report.json -e .` | Passed resolution. |
| Local development requirements | `/tmp/agentforge-py314-compat/bin/python -m pip install --dry-run --report /tmp/agentforge-py314-requirements-report.json -r REQUIREMENTS.txt` | Failed before install. |

The runtime metadata dry-run selected Python 3.14-compatible candidates for the main heavy dependencies, including `chromadb==1.5.9`, `numpy==2.4.6`, `sentence-transformers==5.5.1`, `torch==2.12.0`, `spacy==3.8.13`, and `discord.py==2.7.1`.

## Blockers And Risks

- `REQUIREMENTS.txt` pins optional `matplotlib~=3.9.2`; under Python 3.14, pip selected `matplotlib==3.9.4`, attempted a source build, and failed while preparing/building its NumPy build dependency.
- The failed requirements dry-run did not produce `/tmp/agentforge-py314-requirements-report.json`, so the local development surface is not proven compatible with Python 3.14.
- Runtime metadata resolution pulls a very large Torch/CUDA dependency stack through `sentence-transformers`; this is compatible enough to resolve, but it is a packaging and environment-size risk for Session 4.
- The mismatch between runtime metadata (`chromadb>=1.1.0`) and local requirements (`chromadb==1.0.0`) remains package/install cleanup work.

## Decision

Python 3.14 is under compatibility review, not a claimed supported classifier yet. Keep `python_requires=">=3.10"` and classifiers through Python 3.13 until Python 3.14 can install the full intended development/test surface and run the default pytest suite successfully.

Next compatibility step: during package/install cleanup, split runtime, development, and optional heavy dependencies so Python 3.14 can be validated without forcing every optional multimedia or model dependency into the base environment.
