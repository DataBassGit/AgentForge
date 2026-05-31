# Provider And Modality Baseline

This is a developer-only baseline for provider defaults, modality behavior, and request/response diagnostics. Public `README.md` and hosted `docs/` should be updated only when the supported behavior is ready for user-facing documentation.

## Official References Checked

- OpenAI model catalog, GPT-5.5 pages, Codex model page, and deprecations: https://platform.openai.com/docs/models, https://developers.openai.com/api/docs/models/gpt-5.5, https://developers.openai.com/api/docs/models/gpt-5.5-pro, https://developers.openai.com/api/docs/models/gpt-5.3-codex, and https://developers.openai.com/api/docs/deprecations
- Anthropic model overview, model status, and parameter deprecations: https://docs.anthropic.com/en/docs/about-claude/models/overview and https://platform.claude.com/docs/en/about-claude/model-deprecations
- Gemini model catalog, Gemini 3.5 Flash page, and deprecations: https://ai.google.dev/gemini-api/docs/models, https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash, and https://ai.google.dev/gemini-api/docs/deprecations
- Groq model catalog and model-specific pages: https://console.groq.com/docs/models
- OpenRouter model API guidance: https://openrouter.ai/docs/guides/overview/models

## Provider Decisions

- Keep provider work fake-backed and local. No live provider, credentialed, audio-device, Discord, Ollama server, LM Studio server, or image-generation checks were added to routine verification.
- Keep `text`, `image`, and `audio` as AgentForge capability flags. Unsupported modality errors now name the requested modality and the provider's supported modalities.
- Add `ModelResponseError(ValueError, NonRetriableModelError)` for empty or malformed provider responses. Existing `ValueError` catches still work, while retry loops stop on response shapes that repeated retries will not repair.
- Fail missing `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY`, and `OPENROUTER_API_KEY` before network calls with clear non-retriable messages.
- Keep Codex in `settings/models.yaml` under `openai_api: Codex` so it can be selected through the normal model configuration layer. The OAuth credential flow remains owned by `agentforge.auth.codex_oauth` and `python -m agentforge.init_codex_oauth`.
- Preserve the current base runtime dependency surface. `Pillow` was added only to the optional `other` extra and local optional image requirements because `GeminiVision` imports PIL when image input is used.

## Model Defaults And Parameter Review

- OpenAI GPT defaults now use `max_completion_tokens` instead of stale setup-file `max_tokens`. `OpenAIRuntime.chat_completions()` still maps user/config `max_tokens` to `max_completion_tokens` for backward-compatible overrides.
- OpenAI GPT setup aliases now include the verified `gpt-5.5` and `gpt-5.5-pro` IDs. Deprecated `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`, `o1`, `o1-preview`, `o1-mini`, `o3-mini`, and `o4-mini` setup entries were removed.
- OpenAI Codex remains configured in `models.yaml` with verified `gpt-5.5` and `gpt-5.3-codex` IDs. The older GPT-5.1 and GPT-5.2 Codex entries were removed after OpenAI listed them as deprecated in favor of `gpt-5.5` or `gpt-5.4-mini`; no `gpt-5.5-codex` alias was added because no official supported model ID was found.
- The Codex transport still maps legacy `max_tokens` to `max_output_tokens`, which is the parameter used by the existing OAuth-backed responses request body.
- OpenAI STT/TTS setup aliases now include `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, and `gpt-4o-mini-tts` because the existing wrappers use the same transcription and speech endpoints as the older Whisper/TTS entries.
- Anthropic setup defaults now include the active Claude 4.x IDs verified in provider docs: `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-opus-4-5-20251101`, `claude-opus-4-1-20250805`, `claude-sonnet-4-6`, `claude-sonnet-4-5-20250929`, and `claude-haiku-4-5-20251001`.
- Deprecated or retired Anthropic setup entries were removed: `claude-opus-4-20250514`, `claude-sonnet-4-20250514`, `claude-3-7-sonnet-20250219`, `claude-3-5-haiku-20241022`, and `claude-3-opus-20240229`.
- Anthropic setup defaults now omit `temperature` and `top_p`; Anthropic documents `temperature`, `top_p`, and `top_k` as deprecated for Claude Opus 4.7 and later when set to non-default values. `max_tokens` remains valid for Anthropic Messages API calls.
- Gemini default remains `gemini_api/gemini_flash`, now mapped to stable `gemini-3.5-flash`. `gemini_pro` maps to `gemini-3.1-pro-preview`, `gemini_flash_lite` maps to stable `gemini-3.1-flash-lite`, and `gemini_3_flash_preview` is available for the documented Gemini 3 Flash preview.
- Gemini 2.5 Pro, Flash, and Flash-Lite setup IDs were replaced after Google listed shutdown dates and Gemini 3.x replacements. The image-generation Gemini 3 entries were not added because image generation remains out of scope for this provider pass.
- Gemini setup defaults now use `temperature: 1.0` because Google recommends keeping Gemini 3 models at their default temperature. `max_output_tokens` remains valid for Gemini generation config and was not removed.
- Ollama setup defaults now use `num_predict` instead of top-level `max_tokens`; the adapter sends generation options under Ollama's `options` object. The adapter still maps legacy `max_tokens` to `num_predict` for compatibility.
- Groq setup defaults now use `max_completion_tokens` and canonical stable entries for `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `openai/gpt-oss-120b`, and `openai/gpt-oss-20b`. The adapter maps legacy `max_tokens` to `max_completion_tokens`.
- OpenRouter remains intentionally dynamic. Setup files were not expanded into a broad static catalog because OpenRouter documents hundreds of models and exposes model metadata through its Models API.

## Diagnostics Baseline

- Cloud providers with API-key auth now fail before network calls when the key is missing: Anthropic, Gemini, Groq, and OpenRouter.
- Local/OpenAI-compatible adapters now raise useful provider/model diagnostics for non-200 HTTP responses instead of returning `None`: Ollama, LM Studio, vLLM, and OpenRouter.
- OpenAI-compatible response extraction now raises `ModelResponseError` for missing `choices[0].message.content` rather than leaking `KeyError`/`IndexError` or allowing `None` through as a model reply.
- OpenRouter and Groq now unwrap BaseModel's `{"messages": ...}` payload before sending chat-completion requests.

## Verification Evidence

- Model catalog follow-up: `.venv/bin/python -m pytest tests/config_tests/test_config.py` passed with `5 passed`.
- Gemini catalog follow-up: current Gemini 3.x text-output model IDs were added after checking Google model/deprecation pages; no live Gemini provider call was run.
- `python -c "import pathlib, yaml; yaml.safe_load(pathlib.Path('src/agentforge/setup_files/settings/models.yaml').read_text())"` passed after the model catalog update.
- `.venv/bin/python -m pytest tests/apis_tests tests/multimedia_tests` passed with `42 passed, 1 deselected`.
- `.venv/bin/python -m pytest tests/apis_tests tests/multimedia_tests tests/config_tests tests/agent_tests` passed with `68 passed, 1 deselected`.
- `.venv/bin/python -m pytest` passed with `213 passed, 1 deselected`.
- Scoped Ruff lint and format checks passed on touched Python files.
- Scoped basedpyright passed on touched Python files with `0 errors, 0 warnings, 0 notes`.
- `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` passed.
- `.venv/bin/python -m build --sdist --wheel --outdir /tmp/agentforge-provider-dist` built `agentforge-0.6.5.tar.gz` and `agentforge-0.6.5-py3-none-any.whl`. Sandboxed isolated-build attempts could not resolve PyPI for build dependencies; network-approved reruns succeeded.

## Remaining Risks

- Provider catalogs move quickly. This baseline used conservative stable entries and avoided broad “latest model” chasing; a later provider-catalog review should decide whether AgentForge wants newer defaults such as the latest Anthropic or Gemini families.
- Live provider behavior was not verified. Fake-backed tests prove request shape and local diagnostics, not credentials, quotas, provider availability, or exact remote schema changes.
- The installed `google-generativeai` package emits a deprecation warning recommending migration to `google.genai`. That SDK migration is provider modernization work, but it is larger than this setup-defaults and diagnostics pass.
- Image generation remains roadmap work only. This baseline did not add image-generation provider classes or setup defaults.
- Some compatibility aliases remain in setup defaults to avoid consumer churn where the underlying provider ID is still active, including the legacy-named `claude4_1opus` key. Remove or rename active aliases only in a staged catalog cleanup with migration notes.
