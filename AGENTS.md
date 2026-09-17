# AGENTS.md — layero-agents

Публичный репозиторий `LayeroInfra/layero-agents`: канон того, как агенты
работают с Layero, и сгенерированные из него адаптеры под клиентов.
**Push в `main` виден всем** — секретов, внутренних адресов и черновиков
здесь не бывает.

Сначала прочитай корневой `../AGENTS.md` — необратимые запреты.

## Канон (правится руками)

| Файл | Что это |
|---|---|
| `skills/layero/SKILL.md` + `references/` | Единый навык: что такое Layero, три пути, CLI, MCP, `layero.json`, git-провайдеры |
| `mcp.json` | Как подключить MCP-сервер (`https://mcp.layero.ru/mcp`) |
| `agents-install.json` | Команды установки по клиентам; копии в `frontend/landing` и `layero-docs` сверяются гейтом |
| `SOUL.md` | Принципы поведения агента, отдаётся сервером как `layero://soul` |
| `assets/logo.svg` | Логотип для карточки плагина Cursor |
| `README.md` | Вне блока `<!-- install:start -->…<!-- install:end -->` |

## Генерируется (руками НЕ править)

`.claude-plugin/`, `.cursor-plugin/`, `plugins/**`, `server.json`, `.mcp.json`,
блок установки в `README.md`. Единственный способ их изменить — поправить
канон и выполнить `make build`. Ручная правка проживёт до следующей
генерации и уронит `make check`.

## Команды

```bash
make build   # python3 build-adapters.py — перегенерировать адаптеры
make check   # python3 check-surfaces.py — адаптеры == генерация из канона
```

`make check` обязателен перед пушем. После `make build` рабочее дерево
должно быть чистым, иначе адаптеры разошлись с каноном.

## Правила

- Один факт — одно место: в `skills/layero`. Cursor-правило, копии навыка в
  плагинах и описание в реестре MCP выводятся из него.
- В текстах только `npx layero@latest …`, никаких `npm i -g layero`.
- Адрес MCP, имя сервера `layero`, имя маркетплейса `layero` — не менять.
- Версия адаптеров задаётся в `build-adapters.py` (`VERSION`) и поднимается
  вместе с заметной сменой навыка.
