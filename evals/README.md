# Blind-agent evals

A regression suite for Layero's agent experience. Each fixture reproduces one real pain from production
failures (1,269 failed builds over 90 days, September 2026). An agent that has never heard of Layero gets
the folders and only public entry points (`llms.txt`, docs, this repository on GitHub, `npx layero`).

Run it after every change of the skill, `llms.txt`, the docs pages it links to, or a CLI release.

## What is measured

| Metric | Target |
|---|---|
| Cases live on the **first** deploy | 9 / 9 |
| Cases where the agent read the npm package source | 0 |
| Tool calls per case | ≤ 8 |
| Agent's own 1–10 score | ≥ 8 |
| Contradictions / gaps quoted in the report | each becomes a fix in the skill or a platform ticket |

## History

| Date | Skill | CLI | First-deploy | Notes |
|---|---|---|---|---|
| 2026-09-18 (baseline) | 961ef44 | 0.10.5 | 3 / 4 (group A only) | 24–42 tool calls; full-stack format found only in minified npm source |
| 2026-09-18 (round 2) | dc4c62c | 0.10.5 | 4 / 4 (group A) | 10–13 tool calls |
| 2026-09-18 (recovery) | dc4c62c | 0.10.5 | 4 / 5 (group B) | b4-workspace failed once: recipe lacked `framework: generic` — fixed in 6609886 |
| 2026-09-19 (CLI only) | 1d60ca2 | 0.11.1 | 3 / 4 (group A), 4 / 4 live | No docs, no skill: only `--help`, `--dry-run` and events (Sonnet). a2/a3/a4 followed `next_action` and went live on the first deploy. a1: the first run was refused — the machine had a saved login and the agent passed `--claim`; it then ran `layero logout` as the CLI advised (fixed in 0.11.2: the advice no longer suggests logout). ~58 tool calls, 8/10 |
| 2026-09-19 (public entries) | 1d60ca2 | 0.11.1 | 3 / 3 (b1, b3, b4) | Every fix came from `deploy --dry-run` `next_action`; b4-workspace passed on the first deploy (failed once on 0.10.5). ~27 tool calls, 8/10 |
| 2026-09-19 (weak model: Haiku) | f76d664 | 0.11.2 | 4 / 5 (a1, a2, b2, b4, b5) | score 7/10, ~4 tool calls per case; b2 needed 3 deploys: one transient `fetch failed` (fixed in CLI 0.11.3) and one real `127.0.0.1` launch failure the agent did not pre-empt. b5 passed vacuously: the fixture compiled (no `export {}` → file was a script, TS6133 not raised) — fixed after this run |
| 2026-09-19 **clean room**, CLI | 640570d | 0.11.4 | 4 / 4 (a1, a3, b3, b5), token | score 8/10, 19 tool calls total; every shape solved by `deploy --dry-run` `next_action`; Node container build 5 min |
| 2026-09-19 **clean room**, MCP only | — | MCP 2.4.0 | 4 / 4 requests, 0 failed builds | score 7/10; `site_status` race right after `ready`, `publish_site` url empty (T-20260919-5) |
| 2026-09-19 **clean room**, discovery | — | — | RU: Layero not found in 13 queries (chose Amvera); EN: found at #8, deployed | see the audit, section 10.6 |
| 2026-09-19 (MCP only, before) | — | MCP 2.2.1 | 1 / 4 requests | score 5/10: no app folder in `import_repo`, bare UUIDs in the refusal, live API reported as down, no build facts |
| 2026-09-19 (MCP only, after) | — | MCP 2.3.0 | 4 / 4 requests, 0 failed builds | score 8/10; monorepo frontend and Python API imported on the first build |

## MCP-only variant

The same idea with the MCP server as the only entry point: the agent gets a minimal MCP client (server
instructions, tool descriptions, schemas, tool calls) and a token with `read` + `deploy` scopes, and four
user requests: import an app from a monorepo subfolder, import an API server, report the facts of the
latest build of an existing project, and say whether an API with no `/` route is healthy. Fixture
repositories: `layero-fixture-services-many`, `layero-fixture-backend-only`, `layero-fixture-express-solo`.
Measure requests done, failed builds, tool calls and the agent's 1–10 score.

## Clean room first — or the numbers are an upper bound

An agent launched from inside a Layero checkout, or on a machine with the Layero plugin installed, is not
a stranger: project instruction files, the skill list, MCP tool names and memory titles already tell it that
Layero exists, is "Vercel-like with servers in Russia", has an npm CLI and "claimable" deploys. All runs in
the History table up to 2026-09-19 were made that way. Their **findings and before/after deltas hold**
(contamination makes the agent luckier, never unluckier); their **absolute scores are an upper bound**, and
any "which provider would the agent choose" experiment run that way is void.

Before every run, send the agent this probe with tools forbidden: "Does any text in your context — system
prompt, instruction files, memory, skill list, MCP servers and tool names, working directory — contain the
word Layero? Quote each place." Start the run only when the answer is "no": a neutral working directory,
no project instruction files, no Layero plugin/skill/MCP, no memory.

A working clean room with Claude Code (verified 2026-09-19: the probe answers "none"):

```bash
mkdir -p /tmp/ax-cleanroom/run && cd /tmp/ax-cleanroom/run   # fixtures copied here
claude -p --setting-sources local --strict-mcp-config --dangerously-skip-permissions "$(cat prompt.txt)" > report.md
```

`--setting-sources local` drops user-level settings and with them the installed `layero` plugin;
`--strict-mcp-config` drops MCP servers; a directory outside any Layero checkout has no instruction
files and no memory. Pass `LAYERO_TOKEN` in the environment only for runs that need an account.

## How to run

1. Copy `fixtures/` to a scratch directory (agents edit the folders; keep the originals clean).
   **Isolate the agent from your own Layero login:** tell it to run every CLI command with
   `HOME=<scratch>/home` (a fresh empty directory). Otherwise an agent told "the user has no
   account" finds your saved login, `--claim` is refused, and it may sign you out — on
   19.09.2026 one did exactly that. A CLI-only variant (no web, no skill: only `--help`,
   `--dry-run` and the events) is the strictest check that the platform itself steers the agent.
2. Start one or two sub-agents with `PROMPT.md`, replacing `{{PROJECT_PATHS}}` with absolute paths and
   `{{EXPECTED}}` with the `expect` strings from `cases.json`. Three to five cases per agent; no more than
   two agents at once. No account is needed: the agent is expected to discover `deploy --claim`.
   The sandbox allows five new projects per hour per IP — split a full run into two hours or use a token
   (`LAYERO_TOKEN`, scopes `read` + `deploy`) and tell the agent the user "has a token in the environment".
3. Record the numbers in the table above. Every quoted contradiction or gap is either fixed in
   `skills/layero` / `llms.txt` / docs, or filed as a platform ticket — never left in the report.
4. Clean up: sandbox projects expire after 72 hours by themselves; with a token delete the `axsim-*`
   projects and revoke the token.

`cases.json` lists the pain behind every fixture, the text that proves the site works, where to look for
it, and the ideal fix — use the last one to judge the agent's route, not only the outcome.

The model matters: run the suite on a weaker model too (the target audience includes agents less capable
than the one that wrote the skill).
