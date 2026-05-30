# Core Coding Philosophy

Developer-facing coding guidance for AgentForge, adapted from `/mnt/Data/Abode/agent-configs/rules/core-coding-philosophy.md`. Treat the Abode version as the main reference; this file preserves its structure, intent, and wording except where AgentForge's existing repo conventions require a local adjustment.

Treat this guide as a default review standard, not a loose collection of preferences. Exceptions are allowed when they make the code clearer, but the author or agent should be able to name why the exception is better for the specific change.

## Core Philosophy

Optimize code for human-readable flow. The surface path should be obvious before the details are opened: a reader should be able to scan the top-level structure, understand the end-to-end execution path, and then drill into focused helpers only when needed. Prefer the design that a new reader can understand fastest. Use structure for clarity, not ceremony.

- **Surface the flow, bury the complexity.** High-level orchestration methods should read like a table of contents: a sequence of named method calls in execution order. The body should show what happens next; focused helpers underneath should explain how each step works.

  > **The body is the outline.** If you can't tell what an orchestration method does without reading its helpers, the helpers are misnamed or the steps are wrong.

  This is the default shape for class-like objects, runners, CLIs, workflows, pipelines, and other orchestration-heavy code:

  ```python
  def run(args):
      validate_request(args)
      prepare_inputs(args)
      execute_pipeline(args)
      persist_outputs(args)
      return build_summary(args)

  def execute_pipeline(args):
      run_stage_one(args)
      run_stage_two(args)
      run_stage_three(args)

  def run_stage_one(args):
      # Mid-level orchestration may coordinate modest decisions.
      request = build_provider_request(args)
      response = call_provider(request)
      save_stage_artifacts(response)

  def call_provider(request):
      # Low-level helpers own API calls, parsing, validation, retries,
      # service-specific behavior, and complex branching.
      return provider.generate(request)
  ```

  The exact number of layers should fit the code. Pure functions and small scripts may not need this full shape, but top-level code should still expose intent and order while lower-level helpers own implementation mechanics.
- **Short methods with clear responsibility are good.** Each method should do one understandable thing. A method earns its existence by representing a distinct responsibility, not by containing complex logic or merely forwarding a call.
- **Do not collapse into monolithic methods.** Readability comes from structure, not brevity. Long methods with deeply nested logic and walls of interleaved concerns are harder to follow than well-organized small methods.
- **Do not create meaningless wrappers.** A method that only exists to make another method smaller, without naming a real concern, adds indirection without clarity. Inline it. A single-use helper is still worthwhile when it names a real pipeline step, hides implementation detail, reduces coupling, creates a testable boundary, or makes the high-level flow read cleanly.
- **Consolidate real duplication.** Repeated concepts, validation rules, artifact-building mechanics, fixture setup, path handling, report assembly, provider wiring, or backend-specific translation should have one named home when a shared helper, contract, or module makes the code easier to follow. Do not abstract coincidental similarity; if two blocks only look alike today but serve different responsibilities, keep them local.
- **Decouple components by default.** Pipeline stages, adapters, providers, data stores, report builders, validation, and external services should depend on small contracts or narrow helper APIs instead of each other's internals. Model providers, network clients, storage backends, queues, search, email, payment, or similar external integrations should remain replaceable behind configured boundaries.
- **Group methods into logical sections.** Flow-driving methods, state management, extension points, and supporting helpers should be visually distinct regions within a file. A reader scanning the file should know where to look.
- **Group subclass hooks together.** Methods that exist only to be overridden (`pass`-bodied extension points, lifecycle hooks) belong in their own section so subclass authors can find them at a glance. Do not scatter them through the flow.
- **Keep entry points obvious.** The public interface and high-level orchestration should appear near the top. Supporting detail should appear below, organized by concern.
- **Validate at the boundary.** Check required fields, input formats, supported values, path assumptions, and known preconditions before the main flow begins. Once basic validation has passed, downstream code should not have to keep rediscovering the same assumptions.
- **Keep control flow shallow.** Prefer guard clauses, early returns, early raises, lookup maps, dispatch maps, named decision helpers, policy helpers, strategy-style dispatch, and focused helpers over deep nesting or long conditional chains. `if` statements are welcome when they are the clearest shape; use them intentionally.
- **Cognitive overhead is the enemy.** When choosing between two correct designs, prefer the one where a new reader can understand the flow faster. Fewer file hops, fewer layers of indirection, and fewer anonymous callbacks all reduce cognitive load.
- **Refactoring toward clarity is not rollback.** Simplifying wiring, reorganizing method groupings, or consolidating ceremony is not the same as collapsing structure. Preserve separation of concerns and testability while making the result easier to scan.

## Code Structure

- Prefer simple, local-first tooling over framework-heavy scaffolding unless the project clearly needs the extra structure.
- Keep source code in the active repo's source root, such as `src/` when the repo uses a src layout.
- Keep public entry points and high-level orchestration near the top of the file.
- Put constructors, setup, entry points, and run commands before low-level helpers when that ordering makes the execution path easier to follow.
- Group supporting methods by concern, such as parsing, validation, I/O, diagnostics, and state management.
- Organize folders by hierarchy, scope, jurisdiction, and responsibility. The folder tree should make ownership and system boundaries as clear as the file's internal section layout.
- Mirror source folders in docs and tests wherever practical, so related implementation, documentation, and tests stay isolated by responsibility while remaining easy to navigate.
- Use comment-based section headers when a file has public API plus helpers, multiple responsibilities, or enough length that scanning becomes nontrivial. Tiny single-purpose files do not need ceremony. Names should fit the language, file type, and local style; prefer short labels such as `Main`, `Settings`, `Parsing`, `Validation`, or `Output`.
- Avoid monolithic methods with interleaved concerns, deep nesting, or long stretches of inline mechanics.
- Avoid switch-style branching. In Python, do not use `match` / `case` as a switch statement replacement. Prefer dictionaries, dispatch maps, strategy helpers, or explicitly named functions.
- For simple conditional assignments or values, use concise conditional expressions when they improve readability. Do not use them when they make the code harder to understand.
- Inline helpers that do not add a useful name, reused behavior, or a clearer boundary.
- Refactor toward clarity without flattening distinct responsibilities or undoing testable boundaries.
- **Name length scales with depth.** Top-level and public functions get short, decisive names such as `run`, `load_data`, and `parse_result`. Lower-level helpers get longer, more specific names that announce the action, such as `_initialize_data_attributes`, `_handle_pre_execution_memory`, and `_extract_end_result`. Verb prefixes such as `_initialize_*`, `_handle_*`, `_build_*`, and `_execute_*` make a section's intent scannable.
- **Follow each language's conventions for casing and structure**: Python uses `snake_case` for functions and variables, `PascalCase` for classes, and `UPPER_CASE` for constants. **Use 4-space indentation unless explicitly requested.**
- **Use short, practical docstrings.** Classes, public functions/methods, and most nontrivial private helpers should usually have a brief docstring that explains what they do. One line is enough for simple methods. Add Args or Returns only when they convey something the signature does not. A file where docstrings outweigh the code is a smell.
- **Put multiline docstring opening quotes on their own line.** Single-line docstrings can stay on one line, but multiline docstrings should start with `"""` on a line by itself.
- **Put larger commentary in the file's opening comment block**, not in every method. Module-level summary, ownership, and context belong up top once, not repeated per function.
- **Use inline comments sparingly and deliberately.** Prefer readable code, but add a short comment when it clarifies non-obvious reasoning, invariants, ordering constraints, provider quirks, or intentionally surprising tradeoffs. Do not narrate obvious statements line by line.

### Function And Method Signatures

Prefer function and method definitions to stay on a single line when they fit cleanly within the project's configured maximum line length. Avoid automatically expanding short or moderately sized signatures into multi-line vertical argument lists, because high-level code is easier to scan when the declaration and name remain visually compact.

Use the configured line-length limit as the normal formatting boundary. Multi-line signatures are allowed when a definition genuinely exceeds that limit, when public or heavily typed interfaces are clearer when split, or when the parameter names and defaults would be harder to read on one line.

Do not treat vertical formatting as the main solution for long signatures. A long or repeatedly wrapped signature is usually a design signal: consider grouping related parameters into a dedicated options object, config object, dataclass, request object, or another meaningful domain object before accepting a bloated API shape.

When configuring Ruff for this repo, keep signature formatting aligned with this rule: use Ruff for line-length and signature-adjacent linting, enable `E501`, `PLR0913`, and `UP045`, set the project line length to `120` unless a later phase chooses otherwise, and configure `lint.pylint.max-args` deliberately. BasedPyright should remain focused on type checking and should not enforce formatting or line length.

AgentForge now declares Python `>=3.10`, so touched code should use PEP 604 union syntax such as `str | None` instead of `Optional[str]`. Treat this as staged cleanup for selected files, not a reason to bulk-convert untouched modules during an unrelated session.

### Classes And Abstractions

Use classes when they model a real domain concept, preserve invariants, own lifecycle or state, or make behavior easier to reason about. Domain records, adapters, state objects, positions, profiles, attribution results, and similar objects are good candidates for classes when they clarify responsibility and reduce duplication.

Prefer small, explicit abstractions over premature inheritance. Shared helper modules should come before broad base classes, and focused module-level helpers are usually clearer than static utility classes. Do not add a base class or inheritance hierarchy only because two objects look similar today; wait until the repeated behavior is proven across another artifact family or domain boundary.

Keep contracts, schemas, dataclasses, constants, and other structured definitions near the responsibility they describe. A few local definitions at the top of a module are fine. When definitions are shared, public, sizable, or start to obscure the flow, move them into a responsibility-owned module such as `contracts.py`, `types.py`, or another clearly named sibling file and import them where needed.

Avoid long blocks of setup variables before the reader reaches the module's purpose or execution path. Constants and defaults should have a named home, but the top of a file should not become a catch-all storage area for every detail in the subsystem.

### Code Sections

For files that benefit from navigational markers, prefer a brief opening context comment with useful file metadata, a short summary, and then clear top-level sections. Include only metadata that helps future readers understand ownership, timing, or context; adapt the fields to the language, project, and file type. Files with public API plus helpers, multiple responsibilities, or nontrivial length should usually have meaningful section comments.

```python
"""
Brief summary of what this file does and any context worth knowing.
This is the right place for the larger explanation; it keeps per-method
docstrings short.
"""

# ============================================================
# Public Interface
# ============================================================

# code here

# ============================================================
# Extension Points
# ============================================================
```

Keep sections relatively short. If a section starts needing subsections, split it into clearer top-level sections instead, such as `Input Parsing`, `Validation`, and `Output Writing`. If one section still grows too large, split it again with more specific labels like `Input Parsing - Formats` or `Output Writing - Persistence`. As a last resort, use lightweight one-line separators inside a section.

Use file size as a review gate, not a hard universal cap:

- Around 600 lines, pause and assess whether a clearer module boundary, helper module, contract file, or responsibility-specific file would improve navigation.
- Around 800+ lines, do not add meaningful new code without either extracting a responsibility, creating a split plan, or naming why local growth is clearer for this change.
- Existing oversized files do not need emergency cleanup, but when they are touched, improve the structure where practical or leave an explicit follow-up extraction plan.

### Validation And Error Handling

Validation should happen as early as practical, ideally at module boundaries, public entry points, constructors, parsers, configuration loaders, adapters, and file-system boundaries. Validate required fields, input format, supported file types, supported configuration values, and other known preconditions before the main execution path.

After boundary validation, keep downstream code focused on the main flow. Do not scatter repeated basic validation throughout the execution path if one clear validation point can establish the assumption. Runtime failures can still happen; handle meaningful failure points where they occur, and use early raises or early returns so validation errors do not drag the main logic into nested branches.

## Documentation

Documentation should be useful, concise, and close to the decision it explains. Keep canonical product, architecture, testing, and contributor guidance in the repo's chosen documentation home. Keep implementation notes near the owning source area when they explain local behavior. Prefer links to the canonical source of truth instead of repeating the same guidance in multiple places.

For Markdown docs in this repo, write prose as one line per sentence or paragraph rather than hard-wrapping to a fixed column. Markdown viewers and editors already provide visual wrapping, and preserving source paragraphs makes docs easier to edit. Do not unwrap or reshape code blocks, tables, frontmatter, headings, links, or list structure when normalizing docs.

Short comments are welcome when code has irreducible complexity. Comments should explain why a decision exists, what invariant is being protected, or why an operation must happen in a specific order. If a comment only restates what the next line does, improve the name or structure instead.

## Tests And Verification

- Add tests where behavior is easy to break, shared across modules, or important to users.
- Prefer tests that lock behavior at the boundary that matters to users or downstream callers.
- Use integration or real-output checks when unit tests would miss wiring, file-system, or generated-output behavior.
- Keep verification focused on the risk introduced by the change.
- Test code should follow this philosophy too: make scenario, action, and expected behavior easy to scan, while noisy setup and repeated construction live in well-named helpers or fixtures.

## Change Discipline

- Keep edits scoped to the requested work and the surrounding code that needs to change with it.
- Update docs or tracking notes only when they need to reflect the code change.
- Avoid baking temporary project assumptions into reusable guidance.
- Keep shared coding guidance concise and practical so agents can load it quickly during coding tasks.

## Review Checklist

Before finishing implementation, review the touched code against these defaults:

- Does the top-level flow read like an execution index, with complex mechanics delegated to named helpers or modules?
- Did the change consolidate real duplication or use an existing helper, contract, fixture, provider boundary, or artifact utility where one already fits?
- Are provider-specific, filesystem, storage, report, and artifact mechanics decoupled from unrelated pipeline stages?
- If a touched file is near 600 lines or past 800 lines, did the change improve structure, extract a responsibility, or record why extraction is not part of this change?
- Are condition-heavy decisions expressed with guard clauses, dispatch maps, policy helpers, strategy boundaries, or focused functions where that is clearer than nested branching?
- Are shared contracts, schemas, dataclasses, constants, and setup definitions placed in a responsibility-owned home instead of obscuring the main flow?
- Are docs, docstrings, and inline comments concise, useful, and close to the decision they explain?
