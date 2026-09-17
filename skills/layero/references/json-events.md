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
| `promoted` | `url`, `deploy_id` | Апекс переведён на деплой (`layero promote`, `deploy --promote`). |
| `error` | `code`, `next_action`, `message` | Следовать `next_action`. |

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
