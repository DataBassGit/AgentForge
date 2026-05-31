# Python Compatibility Baseline

Python 3.14 compatibility review. This is developer-only compatibility evidence, not public support documentation.

## Current Python Facts

- Official Python sources list Python 3.14.5 as the latest Python 3 release, released 2026-05-10: https://www.python.org/downloads/latest/ and https://www.python.org/downloads/source/.
- Local default `python --version` and `python3 --version` both reported `Python 3.14.5`.
- The repo-local development environment is now `.venv/` on Python 3.14.
- Package metadata declares `requires-python = ">=3.10"` and includes classifiers through Python 3.14.

## Python 3.14 Evidence

The initial compatibility check used `/tmp/agentforge-py314-compat` so compatibility could be proven before replacing the repo-local Python 3.13 `venv/`.

| Surface | Command | Result |
| --- | --- | --- |
| Runtime/package metadata | `/tmp/agentforge-py314-compat/bin/python -m pip install --dry-run --report /tmp/agentforge-py314-setup-report.json -e .` | Passed resolution. |
| Local development requirements | `/tmp/agentforge-py314-compat/bin/python -m pip install --dry-run --report /tmp/agentforge-py314-requirements-report.json -r REQUIREMENTS.txt` | Passed after dependency cleanup. |
| Optional OCR/image extra | `/tmp/agentforge-py314-compat/bin/python -m pip install --dry-run --report /tmp/agentforge-py314-setup-other-report.json -e '.[other]'` | Passed after optional package-name cleanup. |
| Full local requirements install | `/tmp/agentforge-py314-compat/bin/python -m pip install -r REQUIREMENTS.txt` | Passed after adding tracked pytest dependencies and aligning Chroma to `chromadb>=1.1.0`. |
| Editable package install | `/tmp/agentforge-py314-compat/bin/python -m pip install -e .` | Passed. |
| Default pytest suite | `/tmp/agentforge-py314-compat/bin/python -m pytest` | Passed: `193 passed, 1 deselected`. |

The runtime metadata dry-run selected Python 3.14-compatible candidates for the main heavy dependencies, including `chromadb==1.5.9`, `numpy==2.4.6`, `sentence-transformers==5.5.1`, `torch==2.12.0`, `spacy==3.8.13`, and `discord.py==2.7.1`.

## Dependency Cleanup Follow-Up

Recorded 2026-05-30 after checking whether newer or removable packages could resolve the Python 3.14 blocker.

- `matplotlib~=3.9.2` was the immediate blocker. PyPI listed `matplotlib==3.10.9` with Python 3.14 classifiers during review, and a targeted dry-run for `matplotlib>=3.10,<3.11` resolved on Python 3.14. The repo has no source, test, or docs imports for Matplotlib, so AgentForge removed it from the local requirements and optional extra instead of carrying an unused plotting dependency.
- `umap~=0.1.1` did not resolve for Python 3.14 and had no repo imports. The maintained package is `umap-learn`, but AgentForge does not currently use UMAP, so no replacement was added.
- `REQUIREMENTS.txt` listed `pypdf`, while AgentForge imports `fitz` from PyMuPDF in `src/agentforge/tools/get_text.py`. The local requirements now use `pymupdf`, matching package metadata and the actual runtime import.
- The optional extra used package name `cv2`, but the import is provided by `opencv-python`. The optional extra now uses `opencv-python`, and Python 3.14 dry-run resolution selected `opencv-python==4.13.0.92`.
- Unused direct dependencies `colorama` and `termcolor` were removed from package metadata and `REQUIREMENTS.txt`. `wheel` was moved out of runtime install metadata and remains in local requirements and build-system requirements.
- A duplicate `ruamel.yaml` runtime metadata entry was removed.
- `pytest` and `pytest-timeout` were added to `REQUIREMENTS.txt` so a clean development environment can run the default suite.
- `REQUIREMENTS.txt` now uses `chromadb>=1.1.0`, matching runtime metadata and avoiding the older `chromadb==1.0.0` local-development pin.

## Decision

Python 3.14 is now locally supported for development and default test execution. The repo-local development venv should be `.venv/` on Python 3.14, and the package metadata includes the Python 3.14 classifier.

Keep `requires-python = ">=3.10"` until later compatibility work intentionally changes the lower bound. Do not update public `README.md` or hosted `docs/` with Python 3.14 claims until the final install workflow and documentation surface are verified.

## Remaining Risks

- The local requirements install still pulls a very large Torch/CUDA dependency stack through `torch` and `sentence-transformers`; this is compatible enough to install, but it remains a packaging and environment-size risk.
- The default pytest suite is fake-backed and excludes tests marked `integration`; no live provider, audio, Discord, or storage service checks were run for this compatibility claim.
- Runtime, development, and optional feature dependencies are still conservative and broad across `pyproject.toml` and `REQUIREMENTS.txt`. A later packaging pass should split optional-heavy dependency groups only after adding lazy imports and clearer missing-extra diagnostics.
- Public install docs remain intentionally unchanged until the install and support story is ready for user-facing documentation.
