# R7. Claude Code as the runtime LLM layer: facts that constrain the design

**Research date:** 2026-10-13. **Method:** a `claude-code-guide` subagent read the official Claude Code docs and Anthropic help center pages listed under Sources. Its fetches went through a summarizer, so short quotes are close paraphrases of the official text. Re-check any load-bearing wording before relying on it.

**Labels:** VERIFIED-IN-DOCS = stated on an official page (short quote and source key). SUPPORTED = credible but not official, or reasoning from documented behavior. UNKNOWN = not documented.

## The answer in five lines

1. **Budget is tight.** A Team Standard seat gets 1.25x the Pro per-session allowance, Pro is 1x, and both reset on a rolling five-hour window plus a weekly window. The seat allowance is shared with the user's normal Claude chat use. The nightly LLM layer must be sized for roughly Pro-level usage.
2. **Claude runs only when the user types a command.** The Consumer Terms that govern the Pro plan bar access by "automated or non-human means" except through an API key. Scheduled, unattended Claude runs on the Pro login are a terms risk. Deterministic Python can run on a schedule freely; Claude should not.
3. **No temperature or seed control exists.** Replaying a night must reuse the recorded LLM decisions, not re-ask the model.
4. **Structure is enforceable at the edges.** `claude -p --json-schema` enforces a schema for headless calls. Subagents have no schema field, so a deterministic validator plus a `SubagentStop` hook (exit code 2 keeps the subagent working) rejects malformed output.
5. **Hooks can block writes.** A `PreToolUse` hook that exits with code 2 stops the tool call, which lets deterministic code guard the upload folder.

## 1. Usage limits

- Pro and Max: VERIFIED "a session limit that resets every five hours" [LIM]. Subscriptions have a "rolling usage allowance" [E].
- No absolute message or token counts are published for any plan. VERIFIED absence [LIM, SUP].
- Team Standard: VERIFIED "1.25x the Pro plan's per-session usage allowance"; Team Premium is "6.25x" [TP]. Both have a "rolling five-hour window and a weekly window" [U]. Weekly limits "apply across all models" [TP].
- The Team seat allowance is shared with Claude chat and Cowork [U], so the same person's daytime chat use reduces the nightly budget. SUPPORTED implication.
- Team Standard includes Claude Code. VERIFIED "Claude Code is included with every seat" (post dated January 28, 2026) [BLOG]; Standard is "Base features, usage limits, and Claude Code access" [SEAT].
- Opus costs more. VERIFIED "It uses meaningfully more of your quota" [SUP]. Haiku's exact draw rate: UNKNOWN.
- Subagents cost extra. VERIFIED "every subagent... sends its own requests on top of the main conversation's" [U].
- Each WebFetch runs a separate model call over up to 100,000 characters [T]. Whether web tools count separately against plan limits: UNKNOWN. The help center says "Tools and connectors are token-intensive" [SUP].
- Checking usage: `/usage` shows plan bars with attribution to skills, subagents, plugins, and MCP servers [U]. The statusline JSON exposes `rate_limits.five_hour.used_percentage` and `resets_at`, documented for Pro and Max subscribers [SL]; Team seats are not listed: UNKNOWN.
- At the limit: VERIFIED "Claude Code blocks further requests until the reset time" [E].

## 2. Headless runs and the Agent SDK

- `claude -p` uses the subscription login unless an API key is present; VERIFIED "In non-interactive mode (-p), the key is always used when present" [AU]. An `ANTHROPIC_API_KEY` in the shell silently overrides the login, so the nightly preflight must check for it.
- Useful flags, VERIFIED [H, CLI]: `--output-format json|stream-json`; `--json-schema` (result in `structured_output`); `--max-turns`; `--allowedTools` and `--disallowedTools`; `--permission-mode`; `--model`; `--append-system-prompt`; `--resume`, `--continue`, `--session-id`; `--max-budget-usd` (client-side estimate). JSON output includes `session_id` and `usage`.
- The Python Agent SDK is documented for API keys [QS], and VERIFIED "Anthropic does not allow third party developers to offer claude.ai login" [SDK]. Treat SDK-on-subscription as unsupported. The engine should not depend on the SDK.
- `claude auth status` returns JSON with `authMethod` and `configDirectory` and exits 0 when logged in [CLI]. Use it as a preflight check.

## 3. Subagents

- Defined in `.claude/agents/*.md` (project) or `~/.claude/agents/` (user); project wins on name clashes [SA].
- Frontmatter: `name` and `description` required; `tools` (comma-separated); `model` (sonnet, opus, haiku, fable, a full model ID, or inherit) [SA]. VERIFIED. Choosing a cheaper model per subagent is the main budget lever.
- Background subagents run concurrently, default cap 20 [SA]. VERIFIED.
- Isolation: VERIFIED a subagent "doesn't see your conversation history" [SA]; the parent receives a summary [U]. This gives the QA agent independence from the builder for free.
- No frontmatter field enforces an output schema. Workaround (SUPPORTED): have the subagent write a JSON file, validate it with a deterministic script, and use a `SubagentStop` hook that exits 2 to send it back when invalid [HK].

## 4. Skills and commands

- VERIFIED "Custom commands have been merged into skills" [SK]. `.claude/skills/<name>/SKILL.md` and `.claude/commands/<name>.md` both create `/<name>`.
- Skills support supporting files, `disable-model-invocation`, `allowed-tools`, `model`, `context: fork`, and arguments (`$ARGUMENTS`, `$0`, `$1`, `argument-hint`) [SK].

## 5. Hooks

- Events include SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStop, SessionEnd [HK].
- VERIFIED "Exit with code 2 to block the action" [HK]; stderr becomes the reason shown to Claude. JSON output can return `permissionDecision` allow, deny, ask, or defer.
- Deny rules in settings still win over a hook's allow [P].
- Matchers: a matcher of only letters, digits, `_`, `-`, commas is an exact list; anything else is an unanchored regex. Prefer `Edit,Write` over `Write|Edit` [HK].
- Windows: hooks run in Git Bash if installed, otherwise PowerShell; a `"shell": "powershell"` field exists [HK].

## 6. CLAUDE.md

- Locations: managed policy, `~/.claude/CLAUDE.md`, project `CLAUDE.md`, subdirectory files loaded on demand [M].
- VERIFIED "target under 200 lines per CLAUDE.md file" [M]. Imports with `@path` up to four hops; imports still cost context.
- CLAUDE.md is guidance, not enforcement [M]. Rules that must hold belong in code, hooks, or permission settings.

## 7. Settings and permissions

- Rules evaluate "deny, then ask, then allow" [P]. Examples: `Bash(uv run *)`, `WebFetch(domain:example.com)`, `PowerShell(Get-ChildItem *)`.
- Project allow rules apply after the workspace trust dialog [P]; headless runs need `--allowedTools` or an explicit allow list [H].
- VERIFIED "On native Windows, Claude Code runs commands unsandboxed" [SB]. Permission rules are the only guardrail on this machine.

## 8. Scheduling

- `/loop` fires only while a session is running and idle; recurring tasks expire after seven days [SL].
- Desktop scheduled tasks fire "only... while the app is open and your computer is awake" [R].
- Cloud routines run with the laptop closed but have no local file access and a one-hour minimum interval [SL, R]. Not usable for this engine.
- Windows Task Scheduler can wake the machine (`WakeToRun`) [MS]. Suitable for deterministic Python polling, not for unattended Claude runs (see section 12).

## 9. Web tools

- WebFetch reads up to 100,000 characters per call (roughly 25,000 tokens at most, SUPPORTED arithmetic), caches responses for 15 minutes, and refuses localhost [T]. WebSearch limits: UNKNOWN.

## 10. Determinism and logging

- No temperature or seed flag exists. VERIFIED absence [CLI]. `--effort` is the closest control.
- Transcripts are stored at `~/.claude/projects/<project>/<session-id>.jsonl`; the format is internal and retained 30 days by default (`cleanupPeriodDays`) [SE]. A `SessionEnd` hook receives `transcript_path` [SE].
- Implication: the engine must store its own structured decision records. Transcripts are a debugging aid, not the system of record.

## 11. Token economics

- VERIFIED "a one-line question in a session that has been open all day still draws usage for the whole conversation" [U]. Long-lived nightly sessions get more expensive per command; start fresh sessions for late-swap re-runs.
- Prompt caching: the main conversation gets a one-hour cache on a subscription; subagents get five minutes by default [PC].
- Measure real usage with `--output-format json` `usage` fields or `/usage` before and after a test run [PC, U]. No documented per-fetch figure exists.

## 12. Terms of use (the constraint that matters most)

- Pro is under the Consumer Terms; Team is under the Commercial Terms [L].
- VERIFIED the Consumer Terms bar "automated or non-human means" except "via an Anthropic API Key or where we otherwise explicitly permit it" [CT].
- The docs endorse long-lived subscription tokens (`claude setup-token`) for "CI pipelines and scripts" [AU], which suggests some scripted use is permitted, but the two statements are in tension. Commercial Terms automation clauses: UNKNOWN (the incorporated Usage Policy could not be read) [CMT].
- **Design rule adopted:** every Claude Code run is started by the user typing a command in an interactive session. Nothing schedules Claude. Background polling (injury report, news diffs) is plain Python that alerts the user.

## 13. Two accounts on one laptop

- Each `CLAUDE_CONFIG_DIR` gets its own settings, history, and login [AU]. VERIFIED. Repo-level `.claude/` files (agents, skills, hooks) are shared by both accounts.
- `CLAUDE_CODE_OAUTH_TOKEN` outranks `/login` [AU]; avoid setting it.
- Whether user-level skills and CLAUDE.md move with the config dir: UNKNOWN. Keep everything the engine needs at repo level.

## Implications for the architecture

- Size the nightly LLM work to fit inside one Pro five-hour window with margin, and treat the Team seat as overflow. Measure actual usage on the dry run and record it.
- Use subagents with explicit `model:` (Sonnet for research and QA, Haiku for mechanical parsing) and keep their inputs small: diffs, not full pages.
- All LLM outputs are JSON files validated by deterministic schemas before anything reads them.
- The deterministic validator and exporter are the only writers of the upload file; a `PreToolUse` hook blocks any other write into the uploads folder.
- Replays use stored decision records, never fresh LLM calls.
- Every Claude run is user-initiated.

## Open questions

- Exact weekly caps for Pro and Team Standard (not published). Measure in Phase 1.
- Whether web search and fetch draw from the plan allowance at a different rate.
- Commercial Terms position on scripted use (relevant only if the user ever wants unattended runs).

## Sources

- LIM https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work
- SUP https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code
- E https://code.claude.com/docs/en/errors
- U https://code.claude.com/docs/en/costs
- AU https://code.claude.com/docs/en/authentication
- H https://code.claude.com/docs/en/headless
- CLI https://code.claude.com/docs/en/cli-reference
- SDK https://code.claude.com/docs/en/agent-sdk/overview
- QS https://code.claude.com/docs/en/agent-sdk/quickstart
- SA https://code.claude.com/docs/en/sub-agents
- SK https://code.claude.com/docs/en/skills
- HK https://code.claude.com/docs/en/hooks
- M https://code.claude.com/docs/en/memory
- P https://code.claude.com/docs/en/permissions
- SB https://code.claude.com/docs/en/sandboxing
- SL https://code.claude.com/docs/en/scheduled-tasks
- DST https://code.claude.com/docs/en/desktop-scheduled-tasks
- R https://code.claude.com/docs/en/routines
- MS https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-waketorun
- T https://code.claude.com/docs/en/tools-reference
- SE https://code.claude.com/docs/en/sessions
- PC https://code.claude.com/docs/en/prompt-caching
- L https://code.claude.com/docs/en/legal-and-compliance
- CT https://www.anthropic.com/legal/consumer-terms
- CMT https://www.anthropic.com/legal/commercial-terms
- TP https://support.claude.com/en/articles/9266767-what-is-the-team-plan
- SEAT https://support.claude.com/en/articles/12004354-purchase-and-manage-seats-on-team-plans
- BLOG https://claude.com/blog/claude-team-updates
