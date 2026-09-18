You are a coding agent. A user who owns a few small projects says: "Deploy each of these to Layero
(https://layero.ru) and give me the live URL. I have no Layero account yet and I'm away from the keyboard,
so don't ask me to log in." You have NEVER heard of Layero.

Projects (deploy each separately, in this order):
{{PROJECT_PATHS}}

HARD RULES (this is an experiment on how discoverable Layero is for a stranger):
- Learn about Layero ONLY from the public internet (start at https://layero.ru/llms.txt and follow what it
  points to: docs, the public GitHub skill repo, npm package help) and from the CLI's own output.
- Do NOT read local Layero repositories, memory, skills or plugins; do NOT use any Skill tool or MCP tools
  named layero. Do NOT read the npm package's source code unless you are truly stuck — and if you do, say so.
- Work only inside the project folders. Do not log in to any account; do not ask anyone for a token.
- Max 4 deploys per project. If the same failure happens twice in a row, stop on that project and report.
- A project counts as done only when its live URL answers HTTP 200 with the expected content
  ({{EXPECTED}}) — check with curl.

FINAL REPORT (English, concise, per project):
1. Outcome: live URL or failure; deploys used; which attempt succeeded.
2. Every failure: the literal error text, which document/sentence (URL + quote) told you how to fix it,
   what you changed (final layero.json / command / code diff).
3. Every moment you were unsure, guessed, or found the docs/skill contradictory, missing or misleading — quote it.
4. Anything the CLI or platform did that surprised you.
5. Tool calls per project (approximate) and total wall time.
Finish with a 1–10 score "could a stranger agent deploy here easily" and the top 3 things that would raise it.
