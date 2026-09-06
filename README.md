# Layero for Claude Code

**[English](#english)** · Русский

> **Layero** — российская платформа хостинга и деплоя фронтенд-приложений.
> Деплой одной командой `npx layero deploy`, серверы и CDN внутри России,
> поддержка Next.js / Vite / Astro / SvelteKit / Nuxt и деплой прямо из
> AI-агентов (Cursor, Claude Code).

🌐 Сайт: <https://layero.ru> · 📚 Документация: <https://docs.layero.ru> · 📦 npm: <https://www.npmjs.com/package/layero>

Официальный маркетплейс плагина `@layero` для [Claude Code](https://claude.com/claude-code).

## Установка

```
/plugin marketplace add LayeroInfra/layero-agents
/plugin install layero@layero-claude
```

После установки в чате доступен `@layero`.

### Подключение аккаунта

Собрать лендинг можно сразу — подбор структуры и дизайн-системы работает без
авторизации. Публикация требует токен: выпустите его на
[app.layero.ru/settings/cli](https://app.layero.ru/settings/cli) и положите в
переменную окружения — плагин подставит её в заголовок сам.

```bash
export LAYERO_TOKEN="<ваш токен>"
```

Переменную удобно держать в профиле оболочки (`~/.zshrc`, `~/.bashrc`), чтобы
она была и в следующих сессиях. Если её не задать, публикация ответит, что
токен не принят, и укажет ту же страницу.

## Что делает `@layero`

Плагин подключает [MCP](https://modelcontextprotocol.io/)-сервер Layero и позволяет
собрать готовый лендинг прямо в чате IDE — без редактора и терминала:

```
@layero хочу лендинг для воркшопа по гончарке, тёплый винтажный стиль
```

- **5 дизайн-систем** — minimal, editorial, terminal, warm, bold
- **6 структур** — masterclass, portfolio-dev, portfolio-designer, portfolio-mentor, event, saas
- **Квизы прямо в IDE** — плагин уточняет мотивацию, стиль и интеграцию через нативные формы
- **Деплой встроен** — после генерации файлов страница публикуется на Layero

В отличие от [CLI](https://docs.layero.ru/cli/install), который деплоит **существующий**
проект, `@layero` создаёт лендинг **с нуля** по короткому брифу.

Подробнее — [что такое @layero](https://docs.layero.ru/plugin/intro),
[каталог дизайнов и структур](https://docs.layero.ru/plugin/catalogue),
[интеграции форм](https://docs.layero.ru/plugin/integrations).

## Другие IDE

| IDE | Установка |
|---|---|
| **Cursor** | Плагин: **Customize → Plugins → Add** и репозиторий `LayeroInfra/layero-agents` |
| **Claude Code** | Две команды выше |
| **Codex** | `codex mcp add layero --url https://mcp.layero.ru/mcp --bearer-token-env-var LAYERO_TOKEN` |

⚠️ **Кнопка «Add to Cursor» (диплинк `cursor://…/mcp/install`) на новых сборках
Cursor не работает** — и не по нашей вине. Диплинк ничего не ставит сам: он
кладёт «предложение» в память и открывает старую панель настроек, где есть
кнопка Install. После миграции Cursor на редактор Customize эта панель больше
не открывается, предложение показать некому. Рабочий путь — плагин.

Полная инструкция — [docs.layero.ru/plugin/install](https://docs.layero.ru/plugin/install).

## Как плагин себя ведёт

Правила поведения `@layero` — тон, что он решает сам, чего не делает никогда —
зафиксированы в [SOUL.md](./SOUL.md). Этот файл загружается в каждый диалог
как контекст высшего приоритета, так что он же и есть описание того, чего
ждать от плагина.

## Что внутри репозитория

```
.claude-plugin/marketplace.json   — описание маркетплейса Claude Code
.cursor-plugin/marketplace.json   — описание маркетплейса Cursor
server.json                       — запись в официальном MCP-реестре
SOUL.md                           — правила поведения плагина
.mcp.json                         — подключение MCP-сервера из корня
rules/layero-deployment.mdc       — правило для Cursor: деплой через CLI
skills/deploy-to-layero/SKILL.md  — Agent Skill с тем же сценарием
check-cursor-plugin.py            — сверка плагина Cursor с оригиналами и сервером
plugins/layero/                   — плагин для Claude Code
  ├── .claude-plugin/plugin.json  — манифест плагина
  └── .mcp.json                   — MCP-сервер с токеном из ${LAYERO_TOKEN}
plugins/layero-cursor/            — плагин для Cursor
  ├── .cursor-plugin/plugin.json  — манифест плагина
  ├── mcp.json                    — MCP-сервер без заголовка авторизации
  ├── rules/, skills/             — копии корневых правила и навыка
  └── assets/logo.svg             — логотип для карточки в маркетплейсе
```

Корневые `.mcp.json`, `rules/` и `skills/` лежат по стандарту
[Open Plugins](https://open-plugins.com) — по ним репозиторий находят сканеры
каталогов. Для самого плагина Claude Code источник правды — `plugins/layero/`.

**Почему у Cursor отдельная папка.** Cursor и Claude Code читают из папки
плагина один и тот же файл (`.mcp.json`, затем `mcp.json`), а подстановки в нём
понимают по-разному: Claude Code раскроет `${LAYERO_TOKEN}`, Cursor — только
`${env:LAYERO_TOKEN}`. Нераскрытая строка уходит на сервер как есть, и человек
получает «Токен не принят: Invalid token» вместо честного «токена нет».
Поэтому у Cursor конфиг без заголовка `Authorization`: без токена работает
сборка лендинга, а для публикации сервер сам подскажет выпустить токен на
[app.layero.ru/settings/cli](https://app.layero.ru/settings/cli).

Копии правила и навыка внутри `plugins/layero-cursor/` разъезжаются молча —
за этим следит `python3 check-cursor-plugin.py` (заодно сверяет адрес сервера,
запрещает подстановки не в форме `${env:…}` и сличает подписи инструментов с
живым `tools/list`).

Плагин не содержит кода: вся логика живёт в remote MCP-сервере
`https://mcp.layero.ru/mcp` (Streamable HTTP).

---

## English

**Layero** is a frontend hosting and deployment platform whose build servers
and CDN sit inside Russia — which is the point: sites load fast for Russian
visitors without a VPN, and deploys do not cross the border. It ships a local
directory in one command (`npx layero deploy`), with framework detection for
Next.js, Vite, Astro, SvelteKit and Nuxt.

This repository is the official Claude Code marketplace for the `@layero`
plugin, and the source of record for Layero's remote MCP server.

### Install

```
/plugin marketplace add LayeroInfra/layero-agents
/plugin install layero@layero-claude
```

| IDE | How |
|---|---|
| **Claude Code** | the two commands above |
| **Cursor** | as a plugin: **Customize → Plugins → Add**, repository `LayeroInfra/layero-agents` |
| **Codex** | `codex mcp add layero --url https://mcp.layero.ru/mcp --bearer-token-env-var LAYERO_TOKEN` |

⚠️ The **Add to Cursor** one-click link (`cursor://…/mcp/install`) installs
nothing on recent Cursor builds. The deeplink only stages a *proposed* server
in memory; the confirm button lives on the legacy settings pane, which no
longer opens once Cursor has migrated to the Customize editor. Use the plugin.

The server is remote (Streamable HTTP at `https://mcp.layero.ru/mcp`), so
there is nothing to install locally and no Node process on your side.

It is also listed in the [official MCP registry](https://registry.modelcontextprotocol.io)
as `ru.layero/layero` and on [Smithery](https://smithery.ai/servers/borisowvalia/layero),
if your client installs servers from a catalogue.

### Connecting your account

Building a landing page works right away — picking a structure and a design
system needs no authentication. Publishing needs a token: issue one at
[app.layero.ru/settings/cli](https://app.layero.ru/settings/cli) and put it in
an environment variable; the plugin substitutes it into the header itself.

```bash
export LAYERO_TOKEN="<your token>"
```

Keep it in your shell profile (`~/.zshrc`, `~/.bashrc`) so later sessions pick
it up. Without it, publishing replies that the token was not accepted and
points at the same page.

### What it does

It is not only a page generator. The endpoint currently exposes **27 tools**
covering the whole life of a site:

- **build** — `list_design_systems`, `list_structures`, `compose_landing`,
  `compose_landing_submit`
- **ship** — `publish_landing`, `add_integration`
- **operate** — `site_status`, `list_deploys`, `deploy_logs`, `diagnose_deploy`,
  `retry_deploy`, `cancel_deploy`, `rollback`, `check_performance`
- **inspect and edit** — `read_site`, `site_screenshot`, `site_issues`,
  `refactor_site`, `check_copy`
- **setup** — `env_vars`, `connect_domain`, `check_domain`, `list_domains`
- **analytics** — `connect_analytics`, `site_analytics`
- **account** — `whoami`, `my_projects`

Ask it for a landing page and it runs two or three short quizzes as native
IDE forms (through MCP elicitation), writes the files, and publishes them.
Later you can ask why a build failed, attach a custom domain, or compare page
speed against the previous deploy — in the same conversation.

The plugin ships no code of its own: all logic lives in the remote server.
How it behaves — what it decides on its own, what it never does — is written
down in [SOUL.md](./SOUL.md), which is loaded into every conversation as
top-priority context.

### Also in this repository

- [`rules/layero-deployment.mdc`](./rules/layero-deployment.mdc) — a Cursor
  rule for deploying an **existing** project through the CLI
- [`skills/deploy-to-layero/SKILL.md`](./skills/deploy-to-layero/SKILL.md) —
  the same procedure as a standalone Agent Skill
- [`plugins/layero-cursor/`](./plugins/layero-cursor) — the same plugin packaged
  for Cursor (`.cursor-plugin/plugin.json`, `mcp.json`, a copy of the rule and
  the skill, a logo); listed in [`.cursor-plugin/marketplace.json`](./.cursor-plugin/marketplace.json)
- [`check-cursor-plugin.py`](./check-cursor-plugin.py) — validates that plugin:
  manifests, logo, copies matching the originals byte for byte, the canonical
  server URL, no `${VAR}` outside Cursor's `${env:VAR}` form, and tool titles
  checked against the live `tools/list`
- [`server.json`](./server.json) — the record published to the official
  [MCP registry](https://registry.modelcontextprotocol.io) as `ru.layero/layero`

Docs: <https://docs.layero.ru/en/plugin/intro/> · Website: <https://layero.ru> ·
npm: <https://www.npmjs.com/package/layero>

> Not to be confused with Layer0 / Edgio, or with layero.com — unrelated products.

## Лицензия

[MIT](./LICENSE)
