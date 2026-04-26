**Revised Specification: Codex OAuth via Refactor + Extend of Existing OpenAI Layer**

**1. Design Goals**
1. Implement OpenAI Codex OAuth support without creating a parallel model stack.
2. Refactor existing OpenAI communication code so `GPT`, `O1Series`, `STT`, `TTS`, and new `Codex` share one runtime/auth layer.
3. Preserve AgentForge behavior and integrations (retry/logging/config/model override pipeline).
4. Add module-style login flow aligned with existing pattern (`python -m ...`).
5. Keep implementation clean, testable, and backward compatible.

**2. Core Architecture Decision**
1. Keep OpenAI-family providers in `src/agentforge/apis/openai_api.py`.
2. Extract communication/auth concerns into a shared internal runtime module used by all OpenAI-family classes.
3. Add Codex as a new class in `openai_api.py` that reuses shared runtime with a Codex transport mode.
4. Remove module-level global OpenAI client (`client = OpenAI()`), replace with lazy runtime methods that resolve auth per request.
5. Add OAuth login helper module and CLI module entrypoint.

**3. Why This Is Better**
1. No duplicate provider architecture.
2. Existing OpenAI integrations continue to use the same code path with better client lifecycle handling.
3. Codex-specific HTTP/SSE transport is isolated to one runtime branch, not spread across providers.
4. Future auth modes can be added to the same runtime.

---

**4. Target File Changes**

1. Add `src/agentforge/apis/openai_runtime.py`
2. Modify `src/agentforge/apis/openai_api.py`
3. Modify `src/agentforge/apis/base_api.py`
4. Add `src/agentforge/auth/codex_oauth.py`
5. Add `src/agentforge/auth/__init__.py`
6. Add `src/agentforge/init_codex_oauth.py`
7. Modify `src/agentforge/setup_files/settings/models.yaml`
8. Modify `REQUIREMENTS.txt`
9. Modify `setup.py`
10. Modify docs:
- `docs/guides/installation_guide.md`
- `docs/guides/prerequisites_guide.md`
- `docs/settings/models.md`
- `docs/apis/apis.md`
11. Add tests:
- `tests/apis_tests/test_openai_runtime.py`
- `tests/apis_tests/test_openai_codex_class.py`
- `tests/auth_tests/test_codex_oauth.py`
- Update `tests/multimedia_tests/test_audio_support.py` for new runtime patch points

---

**5. Detailed Implementation**

**5.1 Shared OpenAI Runtime (`openai_runtime.py`)**

Implement a single internal runtime class for OpenAI-family transport/auth:

```python
class OpenAIRuntime:
    def chat_completions(self, model: str, messages: list[dict], params: dict) -> str
    def stt(self, model: str, audio_blob, params: dict) -> str
    def tts(self, model: str, input_text: str, params: dict) -> bytes
    def codex_responses(self, model: str, messages: list[dict], params: dict) -> str
```

Required behavior:
1. `chat_completions`, `stt`, `tts` use OpenAI SDK client created lazily with API-key auth.
2. `codex_responses` uses OAuth token (`oauth_cli_kit`) and direct HTTP streaming against Codex endpoint.
3. No tokens or auth headers logged.
4. Runtime methods raise a dedicated non-retriable error for deterministic setup/auth failures.

Add helper exceptions in runtime:
1. `OpenAIRuntimeError`
2. `OpenAIAuthError(OpenAIRuntimeError)`
3. `OpenAIDependencyError(OpenAIRuntimeError)`

**5.2 BaseModel Non-Retriable Error**

In `src/agentforge/apis/base_api.py`:
1. Add `NonRetriableModelError(Exception)`.
2. In retry loop (`_run_with_retries`), add explicit passthrough:

```python
except NonRetriableModelError:
    raise
```

3. Keep existing retry behavior for transient API/network errors unchanged.

**5.3 OAuth Helper (`auth/codex_oauth.py`)**

Implement:
1. `CodexCredentials` dataclass with `account_id`, `access_token`.
2. `get_codex_credentials(interactive: bool = False, force_reauth: bool = False, print_fn=print, prompt_fn=input) -> CodexCredentials`.

Flow:
1. Import `get_token` and `login_oauth_interactive` from `oauth_cli_kit`.
2. If not forcing reauth, try `get_token()`.
3. If missing token and `interactive=True`, run `login_oauth_interactive`.
4. Validate both `access` and `account_id`.
5. Raise actionable errors:
- missing dependency: install `oauth-cli-kit`
- missing login: run `python -m agentforge.init_codex_oauth`

**5.4 CLI Entry (`init_codex_oauth.py`)**

Create module command:
```bash
python -m agentforge.init_codex_oauth
```

Behavior:
1. Attempt non-force login check + interactive fallback.
2. Print success line with account id.
3. Exit `0` on success, `1` on failure.
4. Handle `KeyboardInterrupt` cleanly.
5. Optional flags:
- `--check`: verify existing token only
- `--force`: force interactive login even if cached token exists

Use `argparse` only.

**5.5 Refactor OpenAI Provider Classes (`openai_api.py`)**

Refactor existing classes to use runtime methods instead of global client:
1. `GPT._do_api_call` delegates to runtime `chat_completions`.
2. `O1Series` keeps current prompt formatting behavior, uses same runtime call.
3. `STT._do_api_call` delegates to runtime `stt`.
4. `TTS._do_api_call` delegates to runtime `tts`.
5. Add new class `Codex(BaseModel)` that:
- accepts standard AgentForge prompt
- delegates to runtime `codex_responses`
- returns text string

Implementation rule:
- Instantiate runtime once per provider instance or as a lightweight module singleton without auth state caching that can stale OAuth tokens.

**5.6 Codex Transport Details (inside runtime)**

Endpoint default:
- `https://chatgpt.com/backend-api/codex/responses`

Headers:
1. `Authorization: Bearer <access_token>`
2. `chatgpt-account-id: <account_id>`
3. `OpenAI-Beta: responses=experimental`
4. `originator: agentforge`
5. `accept: text/event-stream`
6. `content-type: application/json`
7. `User-Agent: agentforge (python)`

Request body baseline:
1. `model`: Codex model identifier
2. `store`: `False`
3. `stream`: `True`
4. `instructions`: extracted system text
5. `input`: converted user message content
6. `text`: `{"verbosity": "medium"}` unless overridden

Message conversion:
1. Preserve current AgentForge two-message format from `BaseModel`.
2. Extract first system content to `instructions`.
3. Convert user content into Codex input_text items.
4. If prompt content is absent, send empty string not `None`.

Parameter handling:
1. Support `max_output_tokens`, `temperature`, `top_p`, `reasoning`, `text`.
2. Map `max_tokens` to `max_output_tokens` when not provided.
3. Accept `host_url`, `timeout`, `verify_ssl` as transport params.
4. Remove transport-only params before body serialization.

SSE parser behavior:
1. Parse `data:` frames separated by blank lines.
2. Ignore `[DONE]`.
3. Handle event types:
- `response.output_text.delta` append delta text
- `response.completed` finalize
- `error` and `response.failed` raise error
4. Ignore unknown event types safely.
5. Return final concatenated text.

Error mapping:
1. HTTP 401/403: “OAuth token invalid/expired; run login command.”
2. HTTP 429: quota/rate-limit message.
3. Other non-200: include status and short response excerpt.
4. Missing credentials/dependency: raise `NonRetriableModelError`.

**6. Config Integration (`models.yaml`)**

Extend existing `openai_api` section in `src/agentforge/setup_files/settings/models.yaml` with `Codex` class:

```yaml
openai_api:
  Codex:
    models:
      codex_gpt51:
        identifier: gpt-5.1-codex
      codex_gpt5_mini:
        identifier: gpt-5-codex-mini
    params:
      max_output_tokens: 10000
      temperature: 0.7
      timeout: 60
      verify_ssl: true
      host_url: https://chatgpt.com/backend-api/codex/responses
```

Important:
1. Keep model keys unique (`codex_*`) so class resolution is deterministic.
2. Do not change existing `GPT`, `O1Series`, `STT`, `TTS` defaults.

**7. Dependencies**

Add `oauth-cli-kit>=0.1.3,<1.0.0` to:
1. `REQUIREMENTS.txt`
2. `setup.py` `install_requires`

No new heavy dependency beyond that.

**8. Documentation Updates**

1. `docs/guides/installation_guide.md`
- Add login command section:
  - `python -m agentforge.init_codex_oauth`
- Place after project init step.

2. `docs/guides/prerequisites_guide.md`
- Add Codex OAuth subsection:
  - Codex does not use `OPENAI_API_KEY`
  - requires interactive OAuth login

3. `docs/settings/models.md`
- Add `openai_api.Codex` config example.
- Document Codex-specific params and `max_tokens -> max_output_tokens` mapping.

4. `docs/apis/apis.md`
- Add row:
  - `Codex` | `openai_api` | OpenAI Codex via OAuth

**9. Tests**

**9.1 `tests/auth_tests/test_codex_oauth.py`**
1. cached token success path.
2. interactive login path invoked.
3. missing dependency error text.
4. non-interactive missing token error text.
5. force reauth ignores cached token.

**9.2 `tests/apis_tests/test_openai_runtime.py`**
1. `chat_completions` calls SDK client with expected params.
2. `codex_responses` builds expected headers/body.
3. SSE delta stream parsed correctly.
4. non-200 mappings (401/403/429/general).
5. `max_tokens` mapping.
6. `verify_ssl` and timeout forwarding.

**9.3 `tests/apis_tests/test_openai_codex_class.py`**
1. `Codex.generate()` returns runtime string output.
2. prompt conversion from BaseModel format works.
3. runtime deterministic auth failure surfaces as `NonRetriableModelError`.

**9.4 Update `tests/multimedia_tests/test_audio_support.py`**
1. Replace monkeypatching of `openai_api.client` with runtime/client-factory monkeypatching.
2. Keep same STT/TTS assertions.

**10. Manual Validation**

1. Install deps.
2. Run `python -m agentforge.init_codex_oauth`.
3. Configure default model to `openai_api` + `codex_gpt51`.
4. Run a simple agent and verify text output.
5. Confirm existing GPT path still works with `OPENAI_API_KEY`.
6. Confirm STT/TTS tests and behavior unchanged.
7. Remove/expire token and verify actionable failure message.

**11. Backward Compatibility and Risk Controls**

1. Existing OpenAI API-key flows remain operational.
2. Existing model config keys remain valid.
3. No changes to config schema format.
4. Main risk is refactor regression in STT/TTS due to client lifecycle change.
5. Mitigation is targeted runtime unit tests + updated multimedia tests.

**12. Definition of Done**

1. Codex OAuth login command works end-to-end.
2. `Codex` model runs via standard AgentForge model pipeline.
3. OpenAI API-key classes (`GPT`, `O1Series`, `STT`, `TTS`) continue working.
4. Tests pass for auth helper, runtime, Codex class, and multimedia compatibility.
5. Docs clearly explain setup and model configuration.
