# Layero для агентов

**[English](#english)** · Русский

> **Layero** — платформа хостинга и деплоя с серверами сборки в России.
> Репозиторий или папка с кодом → сайт на `<проект>.layero.app`; кастомные
> домены, превью-ветки, runtime-приложения, базы Postgres с Data API.

🌐 Сайт: <https://layero.ru> · 📚 Документация: <https://docs.layero.ru/agents/> · 📦 npm: <https://www.npmjs.com/package/layero>

Этот репозиторий — **канон** того, как AI-агенты работают с Layero: один
навык (`skills/layero`), одно описание подключения MCP (`mcp.json`) и одна
таблица команд установки (`agents-install.json`). Всё остальное — плагины
для Claude Code и Cursor, запись в реестре MCP, блок установки ниже —
генерируется из канона скриптом и сверяется гейтом.

## Установка

<!-- install:start -->
MCP: `https://mcp.layero.ru/mcp` (сервер `layero`, транспорт http) · навык: `LayeroInfra/layero-agents`

| Клиент | Команда |
|---|---|
| **CLI** | `npx layero@latest deploy` |
| **Agent Skill** | `npx skills add LayeroInfra/layero-agents` |
| **Любой агент** | `npx -y add-mcp https://mcp.layero.ru/mcp` |
| **Claude Code** | `claude plugin marketplace add LayeroInfra/layero-agents && claude plugin install layero@layero` |
| **Cursor** | `npx -y add-mcp https://mcp.layero.ru/mcp` · [одной кнопкой](https://cursor.com/en/install-mcp?name=layero&config=eyJ1cmwiOiJodHRwczovL21jcC5sYXllcm8ucnUvbWNwIn0%3D) |
| **Codex CLI** | `codex mcp add layero --url https://mcp.layero.ru/mcp` |

CI и бездисплейные среды — токен в `LAYERO_TOKEN`:

```bash
LAYERO_TOKEN=… npx layero@latest deploy --project <slug> --json --yes
```
<!-- install:end -->

Три канала, выбирайте по клиенту:

1. **Навык** — `npx skills add LayeroInfra/layero-agents` ставит `skills/layero`
   в любой агент, понимающий стандарт Agent Skills (`.agents/skills`).
   Навык учит агента трём путям: push в подключённый репозиторий, деплой
   папки через `npx layero@latest deploy --json`, эксплуатация живого сайта.
2. **MCP-сервер** — `npx -y add-mcp https://mcp.layero.ru/mcp` подключает
   удалённый сервер (Streamable HTTP) во все установленные клиенты. Вход —
   OAuth: клиент сам откроет браузер при подключении; для CI — заголовок
   `Authorization: Bearer $LAYERO_TOKEN`. Локально ничего не запускается.
3. **Плагины** — Claude Code (`claude plugin marketplace add LayeroInfra/layero-agents
   && claude plugin install layero@layero`) и Cursor (**Customize → Plugins →
   Add**, репозиторий `LayeroInfra/layero-agents`) ставят навык и MCP одной
   командой.

### CI и среды без браузера

Там, где некому пройти вход в браузере, используется токен `LAYERO_TOKEN`:
выпустите его на [app.layero.ru/settings/cli](https://app.layero.ru/settings/cli)
или командой `npx layero@latest token create`. CLI читает переменную сам;
для MCP плагин Claude Code подставляет её в заголовок
`Authorization: Bearer ${LAYERO_TOKEN}` (то же делает корневой `.mcp.json`
при клонировании репозитория). В плагине Cursor заголовка нет: Cursor не
раскрывает `${VAR}`, и нераскрытая строка ушла бы на сервер как неверный
токен.

## Как агент себя ведёт

Принципы — в [SOUL.md](./SOUL.md): не деплоить на прод молча, показывать
адрес сайта только из ответа платформы, спрашивать человека перед откатом и
выдачей доступа к данным, говорить с пользователем на его языке.

## Структура репозитория

```
skills/layero/SKILL.md            — КАНОН: единый навык
skills/layero/references/         — справочники: JSON-события CLI, layero.json, git-провайдеры
mcp.json                          — КАНОН: как подключить MCP-сервер
agents-install.json               — КАНОН: команды установки по клиентам
SOUL.md                           — принципы поведения агента (layero://soul)
assets/logo.svg                   — логотип для карточки плагина
build-adapters.py                 — генерирует всё ниже
check-surfaces.py                 — гейт: сгенерированное == закоммиченное
.claude-plugin/marketplace.json   — маркетплейс Claude Code          (генерируется)
plugins/layero/                   — плагин Claude Code: .mcp.json + навык (генерируется)
.cursor-plugin/marketplace.json   — маркетплейс Cursor                (генерируется)
plugins/layero-cursor/            — плагин Cursor: mcp.json, правило, навык, логотип (генерируется)
server.json                       — запись в реестре MCP как ru.layero/layero (генерируется)
.mcp.json                         — подключение из корня для Claude Code (генерируется)
```

## Как менять

Правится только канон: `skills/layero/`, `mcp.json`, `agents-install.json`,
`SOUL.md`, этот README вне блока установки. Затем:

```bash
make build   # перегенерировать адаптеры
make check   # убедиться, что всё совпадает
```

Адаптеры руками не правятся — правка проживёт до следующего `make build`
и уронит `make check`. Гейт заодно сверяет копии `agents-install.json` в
соседних чекаутах лендинга и документации, если они есть рядом.

## Где Layero представлен

Единый список внешних адресов. Меняется здесь; каталоги, которые не
обновляются из репозитория сами, помечены — их правят руками после
каждого релиза (гейт `frontend/landing/check-published-claims.py` в `core`
ловит устаревшие обещания).

### Продукт

| Что | Адрес |
|---|---|
| Сайт | https://layero.ru · `llms.txt`: https://layero.ru/llms.txt |
| Панель | https://app.layero.ru |
| Документация | https://docs.layero.ru · для агентов: https://docs.layero.ru/agents/ |
| Статус платформы | https://status.layero.app |
| MCP-сервер | https://mcp.layero.ru/mcp |
| Чат в Telegram | https://t.me/layero_ru |
| Product Radar | https://productradar.ru/product/layero/ |

### Код

| Репозиторий | GitHub | Зеркало GitVerse |
|---|---|---|
| Канон для агентов (этот) | https://github.com/LayeroInfra/layero-agents | https://gitverse.ru/layero/layero-agents |
| CLI (`npm i layero`) | https://github.com/LayeroInfra/cli | https://gitverse.ru/layero/cli |
| Документация | https://github.com/LayeroInfra/layero-docs | https://gitverse.ru/layero/layero-docs |
| Примеры | https://github.com/LayeroInfra/examples | https://gitverse.ru/layero/examples |
| GitHub Action | https://github.com/LayeroInfra/deploy-action | https://gitverse.ru/layero/deploy-action |
| Дизайн-система | https://github.com/LayeroInfra/design-system | https://gitverse.ru/layero/design-system |

Организация на GitVerse — https://gitverse.ru/layero. Зеркала обновляются
workflow `mirror-gitverse.yml` в каждом репозитории при push в `main`
(CLI — из `publish-cli.yml` в `core`); нужны секреты `GITVERSE_LOGIN` и
`GITVERSE_TOKEN` на уровне организации GitHub.

### Пакеты и маркетплейсы

| Площадка | Запись | Обновляется |
|---|---|---|
| npm | https://www.npmjs.com/package/layero | публикацией тега `cli-v*` |
| GitHub Marketplace | https://github.com/marketplace/actions/deploy-to-layero | релизом `deploy-action` |
| Официальный реестр MCP | `ru.layero/layero` — https://registry.modelcontextprotocol.io/v0.1/servers?search=ru.layero | `mcp-publisher publish` из `mcp/` (бамп версии обязателен) |
| Claude Code marketplace | `claude plugin marketplace add LayeroInfra/layero-agents` → `layero@layero` | из этого репозитория |
| Cursor marketplace | `.cursor-plugin/marketplace.json` этого репозитория | из этого репозитория |
| skills.sh | https://skills.sh/LayeroInfra/layero-agents | из этого репозитория |
| Smithery | https://smithery.ai/servers/borisowvalia/layero | **руками**: `npx @smithery/cli mcp publish https://mcp.layero.ru/mcp -n borisowvalia/layero`, описание в Settings |
| Glama | https://glama.ai/mcp/connectors/ru.layero/layero | из реестра MCP; владение подтверждено файлом https://mcp.layero.ru/.well-known/glama.json |
| cursor.directory | https://cursor.directory/plugins/layero | **руками** на `/plugins/layero/edit` |
| mcp.so | заявка https://github.com/chatmcp/mcpso/issues/4219 | по заявке |
| PulseMCP | берёт из реестра MCP | автоматически |

---

## English

**Layero** is a hosting and deployment platform whose build servers sit
inside Russia: connect a repository or ship a directory, get a site at
`<project>.layero.app`, plus custom domains, branch previews, runtime apps
and Postgres databases with a Data API.

This repository is the **canonical source** for how AI agents work with
Layero: one skill (`skills/layero`), one MCP connection spec (`mcp.json`) and
one table of install commands (`agents-install.json`). Everything else — the
Claude Code and Cursor plugins, the MCP registry record, the install block
above — is generated from the canon and checked by a gate.

### Install

Commands per client are in the table above (`agents-install.json`). Three
channels:

1. **Skill** — `npx skills add LayeroInfra/layero-agents` installs
   `skills/layero` into any agent that reads the Agent Skills standard.
2. **MCP server** — `npx -y add-mcp https://mcp.layero.ru/mcp` adds the remote
   server (Streamable HTTP) to every installed client. Sign-in is OAuth; the
   client opens the browser itself. Nothing runs locally.
3. **Plugins** — Claude Code (`claude plugin marketplace add LayeroInfra/layero-agents
   && claude plugin install layero@layero`) and Cursor (**Customize → Plugins →
   Add**, repository `LayeroInfra/layero-agents`).

### CI

Where nobody can sign in through a browser, use `LAYERO_TOKEN`: issue it at
[app.layero.ru/settings/cli](https://app.layero.ru/settings/cli) or with
`npx layero@latest token create`.

```bash
LAYERO_TOKEN=… npx layero@latest deploy --project <slug> --json --yes
```

The CLI reads the variable itself; the Claude Code plugin (and the root
`.mcp.json`) forward it as `Authorization: Bearer ${LAYERO_TOKEN}`. The Cursor
plugin ships no header because Cursor does not expand `${VAR}`.

### Changing things

Edit only the canon (`skills/layero/`, `mcp.json`, `agents-install.json`,
`SOUL.md`, this README outside the install block), then `make build` and
`make check`. Generated adapters are never edited by hand.

Docs: <https://docs.layero.ru/en/agents/> · Website: <https://layero.ru> ·
npm: <https://www.npmjs.com/package/layero>

> Not to be confused with Layer0 / Edgio, or with layero.com — unrelated products.

## Лицензия

[MIT](./LICENSE)
