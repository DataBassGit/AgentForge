# Test Review Baseline

Recorded 2026-05-30 for Phase 1, Session 2. This is a deterministic review baseline for staging test cleanup, not a full test-suite audit.

## Collection Baseline

- Default collection before Session 2: `192/193` tests selected, with one integration-marked test deselected by `pytest.ini`.
- Default collection after Session 2: `193/194` tests selected, with one integration-marked test deselected by `pytest.ini`.
- Integration marker before Session 2: only `tests/multimedia_tests/test_vision_support.py::TestGeminiVision::test_real_image_processing`.
- Integration marker after Session 2: unchanged; only `tests/multimedia_tests/test_vision_support.py::TestGeminiVision::test_real_image_processing`.
- `tests/integration_tests/test_example_cog_with_personamemory.py` contains five fast fake-backed cross-component workflow tests and intentionally remains in the default suite.
- `tests/integration_tests/test_persona_memory_integration.py` contained only fixtures before Session 2, so it collected no tests; it now collects one fast fake-backed PersonaMemory workflow test.

## Marker Policy Decision

Keep fast fake-backed cross-component tests in the default suite when they protect realistic framework wiring without live services. Use `integration` for live, credentialed, service-backed, slow, or stochastic tests. Keep `tests/real_tests/` as manual live scripts, not routine verification.

## Harness Findings

| Area | Finding | Session 2 action |
| --- | --- | --- |
| Repo-root `.agentforge` | `bootstrap_test_env()` may create repo-root config, while normal tests should prefer `isolated_config`. | Preserve explicit `Config.reset(root_path=...)` handling in the bootstrap patch so `isolated_config` uses its temporary `.agentforge` tree. |
| Duplicate import path setup | Multimedia tests repeated `src/` path insertion even though shared bootstrap already handles it. | Remove duplicate path setup from touched multimedia tests. |
| Integration marker accuracy | One live vision test is correctly marked; fake-backed cross-component tests remain default coverage. | Document marker policy instead of moving fast fake-backed tests out of the default suite. |
| Noisy/ceremonial tests | Some `ConfigManager` validation checks used try/except, `assert False`, and print-only success messages. | Convert the validation checks touched in Session 2 to `pytest.raises(..., match=...)`. |
| Fixture-only test module | `test_persona_memory_integration.py` had useful setup but no collected assertions. | Add one fake-backed workflow test that proves the fixture exercises PersonaMemory query/update agents. |

## Review Records

| Test or group | Supported behavior | Failure caught | Boundary | Fixture/live policy | Action |
| --- | --- | --- | --- | --- | --- |
| `tests/config_tests/test_config_manager_phase1.py::test_config_manager_validation` | Invalid agent and Cog config fail with actionable `ValueError` messages. | Missing required fields accidentally accepted or diagnostics changed into opaque failures. | Config loader and validation. | Fake-backed default. | Updated to direct `pytest.raises` assertions. |
| `tests/multimedia_tests/test_audio_support.py` | Audio modality flags, unsupported-audio rejection, STT/TTS wrappers, and audio-file save behavior. | Live SDK calls, unsupported modality gaps, or broken audio persistence. | Provider adapter and Agent audio helper. | Fake-backed default. | Removed duplicate path setup and narrowed optional audio manager assertion. |
| `tests/multimedia_tests/test_vision_support.py` | Vision modality flags, GeminiVision inheritance, request part merging, and optional live image behavior. | Text-only models accepting images, vision model losing image support, or live image check running without credentials. | Provider adapter and modality mixin. | Fake-backed default plus one integration-marked live test. | Removed duplicate path setup and replaced import-only Pillow check. |
| `tests/integration_tests/test_persona_memory_integration.py` | PersonaMemory participates in a Cog workflow and invokes retrieval, narrative, and update agents with fake storage. | PersonaMemory fixture drift, memory trigger wiring regression, or dead fixture module collecting no tests. | Cog flow and storage/memory contract. | Fast fake-backed default. | Added one collected workflow test. |
| `src/agentforge/testing/bootstrap.py` | Shared test bootstrap can create repo-root config for scripts while still allowing explicit temporary roots in tests. | Order-dependent tests caused by `isolated_config` silently using repo-root `.agentforge`. | Test helper. | Fake-backed default. | Restored explicit root-path handling in the bootstrap patch. |

## Session 8 Follow-up

Recorded 2026-05-31 after the scoped config/Cog/core test cleanup.

- `tests/config_tests/test_config_manager_phase1.py` no longer emits print-only success output; assertions remain the test proof.
- `tests/cog_tests/test_cog_trail_logging_and_flow_validation.py` now asserts parsed Cog flows are present before accessing flow members, matching the behavior under test and satisfying static narrowing.
- `tests/core_tests/test_memory_manager.py` keeps the defensive non-dict `get_dot_notated` check while marking the invalid input as intentionally untyped for static analysis.
- Focused Session 8 tests passed with `31 passed`, and the full default suite passed with `225 passed, 1 deselected`.

## Deferred Cleanup

- Review whether `tests/conftest.py` and `src/agentforge/testing/bootstrap.py` should share one Agent-run stub instead of maintaining parallel behavior.
- Continue replacing print-only success messages in tests outside the Session 8 scope when those files are touched for substantive reasons.
- Review `tests/real_tests/` separately before deciding whether any manual live script should become a marked integration test.
