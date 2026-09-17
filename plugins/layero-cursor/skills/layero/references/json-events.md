# JSON-события Layero CLI

Полный справочник: <https://docs.layero.ru/cli/json-events> (en:
<https://docs.layero.ru/en/cli/json-events>). Здесь — то, что нужно агенту
при деплое.

Режим включается флагом `--json`, переменной `LAYERO_JSON=1`, а также сам —
внутри агента или при не-TTY stdout. В этом режиме CLI не задаёт вопросов
(для `--prod` всё равно нужен `--yes`), печатает по одной строке
`{"event": "...", "ts": "<ISO-8601>", ...}` на действие, ошибки приходят со
стабильным `code` и `next_action`.

## События деплоя

| событие | поля | что делать |
|---|---|---|
| `auth_required` | `url`, `user_code` | Показать `url` кликабельной ссылкой. CLI поллит каждые 2 с, токен кэшируется в `~/.layero/config.json`. Callback на localhost нет — браузер может быть на другой машине. Истечение — `error{auth_expired \| auth_timeout}`. |
| `authorized` | `user` | Вход успешен. |
| `project_created` | `project_id`, `slug`, `organization` | Первый деплой в папке — создан проект. |
| `project_linked` | `project_id`, `slug` | Деплой в проект из `.layero/project.json`. |
| `detected` | `framework`, `build_cmd`, `output_dir`, `confident` | Информационно. Не переопределять, если детект не ошибся явно. `confident: false` — static-fallback. |
| `packing` | `files`, `bytes`, `sha256` | Папка упакована в tar.gz. |
| `uploading` / `uploaded` | `archive_key` | Заливка архива. |
| `prebuilt` | `dir` | Деплой готовой сборки (`--prebuilt <dir>`), сборка на платформе пропускается. |
| `runtime_type_applied` | `project_type` | Проект определён как runtime-приложение (`ssr_next`, `node_web`, `python_web`, `streamlit`, `gradio`, `flask`). |
| `runtime_type_apply_failed` | `error` | Тип не проставился, деплой идёт с прежним. |
| `setup_applied` | — | Настройки проекта применены на первом деплое. |
| `repeated_failure_guard` | `streak`, `threshold`, `scope`, `failure_stage`, `error` | Подряд идущие сборки падают с одной ошибкой — платформа остановилась. Прочитать `error`, устранить причину. Автоматически продолжить нельзя. |
| `deploy_started` | `deploy_id` | Бэкенд принял задачу. |
| `stage` | `name`: `clone`/`install`/`build`/`upload`/`activate` | Стадия сборки. |
| `build_log` | `line`, `stream` | Сырой лог. Пересылать только строки с ошибками. |
| `ready` | `url`, `dashboard_url`, `deploy_id` | **Финал.** `url` — живой публичный адрес, показать как есть и остановиться. `dashboard_url` — панель, не сайт. `preview_url`, `edge_ready`, `edge_eta_seconds` — legacy, не ждать. |
| `claimable` | `project_id`, `slug`, `url`, `claim_url`, `expires_at` | Деплой без аккаунта (`--claim`): временный проект на 72 часа. Приходит **до** `ready`. Передать человеку `claim_url` — забрать сайт может только он, в панели. |
| `promoted` | `url`, `deploy_id` | Апекс переведён на деплой (`layero promote`, `deploy --promote`). |
| `error` | `code`, `next_action`, `message` | Следовать `next_action`. |

## События остальных команд

| событие | команда | поля |
|---|---|---|
| `me` | `whoami` | `id`, `username`, `email`, `github_login` |
| `projects` | `projects list` | `projects[]`: `id`, `slug`, `name`, `organization`, `url`, `source_type`, `repo`, `status` |
| `organizations` | `orgs list` | `organizations[]`: `id`, `slug`, `kind`, `role` |
| `project_created` | `projects create --repo` | как у деплоя, плюс `url`, `repo`, `branch` |
| `source_connected` | `sources connect`, `projects create` | `org`, `connection_id`, `provider`, `account` |
| `webhook_installed` / `webhook_unavailable` | `projects create` | `project`, `url` (у GitHub App поля `url` нет: вебхук — часть установки); у `webhook_unavailable` — `hint`. Без вебхука push не собирается — сказать человеку, дать `url` для ручной настройки. |
| `setup_applied` | `projects create` | `project`, `framework`, `build_cmd`, `output_dir`, `layero_found`. Команда сама применила настройки из детекта — как кнопка «Начать деплой» в панели; за ним идёт `deploy_started` |
| `deploy_started` | `projects create`, `deploy` | `deploy_id`; у `projects create` ещё `project`, `url`. Первая сборка запущена — дальше `deploys list --project <slug>` или MCP `site_status` |
| `setup_pending` | `projects create --no-deploy` | `project`, `url`, `hint`. Проект оставлен в мастере: сборок не будет, пока человек не завершит настройку по `url` |
| `setup_failed` | `projects create` | `project`, `reason`, `url`, `hint`. Проект **создан** (выход 0), но детект, настройка или запуск сборки не удались — сказать человеку завершить в панели по `url` |
| `sources` | `sources list` | `org`, `providers[]` (`id`, `title`, `self_hosted`, `webhook_supported`, `token_hint`), `connections[]` (`id`, `provider`, `account`, `status`, `projects_count`, `token_expiry_state`, `last_error`) |
| `source_repos` | `sources repos` | `org`, `connection_id`, `repos[]` (`path`, `name`, `default_branch`, `private`, `can_admin`) |
| `environments` | `envs list` | `project`, `environments[]` (`id`, `branch`, `url`, `hostname`, `active_deploy_id`, `active_deploy_at`, `production`) |
| `project_deleted` | `projects delete --yes` | `project_id`, `slug` |
| `project_linked` | `link` | `project_id`, `slug`, `url`, `status` |
| `hooks` / `hook_created` / `hook_deleted` | `hooks *` | `project`, `hooks[]` / `id`, `name`, `branch`, `target`, `url` / `id` |
| `init_done` | `init` | `framework`, `agent_docs[]` (`file`, `result`), `project_json` |
| `logged_out` | `logout` | `config_path` |
| `claim_status` | `claim status` | `code`, `status`, `claimed`, `expires_at`, `url`, `claim_url` |
| `claim_accept` | `claim accept` | `code`, `claim_url`, `opened` — в агентском режиме браузер не открывается, ссылку показать человеку |

События `data_*` (Data API: `layero data …`) описаны в полном справочнике.

## Коды `error`, которые встречаются при деплое

| `code` | когда | `next_action` |
|---|---|---|
| `auth_required` | Нет токена ни в `~/.layero/config.json`, ни в `LAYERO_TOKEN` | `layero login` или задать `LAYERO_TOKEN` |
| `auth_expired` | `user_code` истёк (15 мин) или сохранённый токен протух (7 дней) / отозван — API ответил 401 | `layero login` ещё раз |
| `auth_timeout` | 15 минут поллинга без подтверждения | `layero login` ещё раз |
| `plan_limit` | Лимит тарифа (API 402) | Тариф на `app.layero.ru/billing` или удалить лишнее |
| `username_required` | У аккаунта не выбрано имя (API 412); в агентском режиме спросить некого | `layero username <имя>` |
| `username_rejected` | Имя занято или не по формату | Строчные латинские, цифры, дефис, 2–32 символа |
| `oauth_unavailable` | Провайдер входа недоступен | Позже |
| `project_unknown` | Вне каталога проекта и без `--project` | Из каталога проекта или `--project <id\|slug>` |
| `project_not_found` | `--project` на несуществующий проект | `layero projects list` |
| `cli_deploys_disabled` | CLI-деплои выключены в проекте | Project Settings → CLI deploys |
| `invalid_type` | Неизвестный `--type` | Убрать флаг или валидный пресет |
| `invalid_choice` | Невалидный выбор в non-TTY | Явный флаг |
| `branch_unsupported` | `deploy --branch`: архив всегда идёт в окружение `cli`, флаг превью не даёт. Ничего не загружено | Подключить репозиторий (`projects create --repo`) и пушить в ветку; у проекта с репозиторием в `next_action` — куда пушить |
| `repo_format` / `account_not_found` / `repo_not_found` / `repo_already_imported` / `source_connect_failed` | `projects create --repo`: формат, нет подключения к провайдеру, репозиторий не виден, уже привязан, привязка сорвалась | `next_action`: `sources list`, `sources connect`, `sources repos`, `link` |
| `provider_unknown` / `token_missing` / `source_rejected` / `connection_not_found` | `sources connect` / `sources repos` | Список провайдеров, `--token-stdin`, `token_hint` провайдера, `sources list` |
| `hook_not_found` | `hooks delete` с чужим id | `hooks list` |
| `claimable_unavailable` | Деплой без аккаунта не включён на платформе | `layero login` или `LAYERO_TOKEN` |
| `claim_unknown` | Нет заявки в `.layero/project.json`, код неверный или истёк | Передать код; новый — `deploy --claim` |
| `prebuilt_no_dir` / `prebuilt_no_index` | Папка `--prebuilt` не найдена / без `index.html` | `--prebuilt ./dist` со собранным `index.html` |
| `deploy_not_started` | Сборка не стартовала | Повторить; если повторяется — проект в панели |
| `deploy_failed` | Сборка не дошла до `ready` | Логи по ссылке из `next_action` |
| `deploy_cancelled` | Сборка отменена | — |
| `repeated_failure` | Повтор одной и той же ошибки, платформа отказалась выкатывать вслепую | Устранить причину; если уже устранена — `--confirm-repeated-failure` |
| `forbidden` | Токену CI (`layero_ci_*`) не хватает scope | Выпустить токен с нужным scope |
| `org_unknown` | Несколько организаций, команда не знает, в какой работать | `--org <slug>`; список — `layero orgs list` |
| `confirmation_required` | Команда меняет доступ, а подтвердить в агентском режиме некому; ничего не изменено | Показать план человеку и повторить с `--yes` |
| `internal` | Непредвиденная ошибка CLI | Перезапустить с `--debug` |

Код неуспешного деплоя собирается как `deploy_<status>`, статусов четыре:
`ready`, `building`, `failed`, `cancelled`. На практике встречаются ровно
`deploy_failed` и `deploy_cancelled`; кодов `deploy_error` и
`deploy_timed_out` не существует — не закладывайся на них.

## Коды выхода

| код | класс | примеры |
|---|---|---|
| 0 | успех | |
| 1 | прочее | `plan_limit`, `forbidden`, `confirmation_required`, `repeated_failure` |
| 2 | нужен вход | `auth_required`, `auth_expired`, `auth_timeout` |
| 3 | не найдено | `project_unknown`, `project_not_found`, `org_unknown`, `hook_not_found`, `claim_unknown` |
| 4 | неверный ввод | `invalid_type`, `prebuilt_no_dir`, `prebuilt_no_index`, `branch_unsupported`, `repo_format`, `token_missing` |
| 5 | удалённая ошибка | `deploy_failed`, `deploy_cancelled`, `deploy_not_started`, `internal`, `http_5xx` |

## Минимальный поведенческий блок

```text
If user asks to deploy via Layero:
  1. Run: npx layero@latest deploy --json
  2. Parse each stdout line as JSON, route on .event:
     - "auth_required" → render .url as clickable link, keep waiting
     - "ready" → show .url (the live site) to user; it is reachable
                 right away — do NOT gate on .edge_ready. Then stop.
     - "error" → follow .next_action verbatim
  3. Never run `git init`. Never run `npm install -g layero`.
```
