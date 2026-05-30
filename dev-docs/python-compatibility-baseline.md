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
| Local development requirements | `/tmp/agentforge-py314-compat/bin/python -m pip install --dry-run --report /tmp/agentforge-py314-requirements-report.json -r REQUIREMENTS.txt` | Initially failed before install; passed after the dependency cleanup follow-up below. |
| Optional OCR/image extra | `/tmp/agentforge-py314-compat/bin/python -m pip install --dry-run --report /tmp/agentforge-py314-setup-other-report.json -e '.[other]'` | Initially failed through stale optional metadata; passed after the dependency cleanup follow-up below. |

The runtime metadata dry-run selected Python 3.14-compatible candidates for the main heavy dependencies, including `chromadb==1.5.9`, `numpy==2.4.6`, `sentence-transformers==5.5.1`, `torch==2.12.0`, `spacy==3.8.13`, and `discord.py==2.7.1`.

## Dependency Cleanup Follow-Up

Recorded 2026-05-30 after checking whether newer or removable packages could resolve the Python 3.14 blocker.

- `matplotlib~=3.9.2` was the immediate blocker. PyPI lists `matplotlib==3.10.9` with Python 3.14 classifiers, and a targeted dry-run for `matplotlib>=3.10,<3.11` resolved on Python 3.14. The repo has no source, test, or docs imports for Matplotlib, so AgentForge removed it from the local requirements and optional extra instead of carrying an unused plotting dependency.
- `umap~=0.1.1` did not resolve for Python 3.14 and had no repo imports. The maintained package is `umap-learn` (`0.5.12` at the time of review), but AgentForge does not currently use UMAP, so no replacement was added.
- `REQUIREMENTS.txt` listed `pypdf`, while AgentForge imports `fitz` from PyMuPDF in `src/agentforge/tools/get_text.py`. The local requirements now use `pymupdf`, matching `setup.py` and the actual runtime import.
- The optional extra used package name `cv2`, but the import is provided by `opencv-python`. The optional extra now uses `opencv-python`, and Python 3.14 dry-run resolution selected `opencv-python==4.13.0.92`.
- Unused direct dependencies `colorama` and `termcolor` were removed from `setup.py` and `REQUIREMENTS.txt`. `wheel` was removed from runtime install metadata but remains in local requirements as development/build tooling.
- A duplicate `ruamel.yaml` runtime metadata entry was removed.

After these changes, the Python 3.14 dry-runs for `-e .`, `-e '.[other]'`, and `-r REQUIREMENTS.txt` all passed. This is resolution evidence only; it is not a successful full install or test run in Python 3.14.

## Blockers And Risks

- Python 3.14 full support is still unclaimed because the compatibility venv has not installed the full dependency set and has not run the default pytest suite.
- The local requirements dry-run still pulls a very large Torch/CUDA dependency stack through `torch` and `sentence-transformers`; this is compatible enough to resolve, but it is a packaging and environment-size risk for Session 4.
- `REQUIREMENTS.txt` still pins `chromadb==1.0.0`, while runtime metadata uses `chromadb>=1.1.0`. The Python 3.14 dry-run for the local requirements passes, but it includes a source distribution for `chroma-hnswlib==0.7.6`, so install/build behavior is not yet proven.
- The mismatch between runtime metadata (`chromadb>=1.1.0`) and local requirements (`chromadb==1.0.0`) remains package/install cleanup work.

## Decision

Python 3.14 is under compatibility review, not a claimed supported classifier yet. Keep `python_requires=">=3.10"` and classifiers through Python 3.13 until Python 3.14 can install the full intended development/test surface and run the default pytest suite successfully.

Next compatibility step: during package/install cleanup, split runtime, development, and optional heavy dependencies so Python 3.14 can be validated without forcing every optional multimedia or model dependency into the base environment. If the Chroma/model stack remains large but compatible, keep it as an AgentForge dependency only where the storage/embedding features require it; a separate venv is more appropriate for live model or heavyweight optional workflows than for core package metadata.
