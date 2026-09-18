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
| 2026-09-19 (MCP only, before) | — | MCP 2.2.1 | 1 / 4 requests | score 5/10: no app folder in `import_repo`, bare UUIDs in the refusal, live API reported as down, no build facts |
| 2026-09-19 (MCP only, after) | — | MCP 2.3.0 | 4 / 4 requests, 0 failed builds | score 8/10; monorepo frontend and Python API imported on the first build |

## MCP-only variant

The same idea with the MCP server as the only entry point: the agent gets a minimal MCP client (server
instructions, tool descriptions, schemas, tool calls) and a token with `read` + `deploy` scopes, and four
user requests: import an app from a monorepo subfolder, import an API server, report the facts of the
latest build of an existing project, and say whether an API with no `/` route is healthy. Fixture
repositories: `layero-fixture-services-many`, `layero-fixture-backend-only`, `layero-fixture-express-solo`.
Measure requests done, failed builds, tool calls and the agent's 1–10 score.

## How to run

1. Copy `fixtures/` to a scratch directory (agents edit the folders; keep the originals clean).
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
