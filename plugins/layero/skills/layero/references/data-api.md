# Data API, sign-in and files — the path for an agent

Layero gives a Postgres database a Supabase-compatible HTTP API: tables and
functions (`/rest/v1`), sign-in (`/auth/v1`) and files (`/storage/v1`) at
`https://data.layero.ru/<database>`. Use the regular
`@supabase/supabase-js@2` client; there is nothing Layero-specific to learn
on the client side.

Data API, sign-in and files are an experimental feature available on the Pro
plan (and to organizations in the beta list). On the free plan, enabling
them answers `402` with an upgrade offer — tell the person, do not retry.

## The path: database → table with RLS → sign-in → files

| Step | Who | How |
|---|---|---|
| 1. Database | agent | `npx layero@latest db create <name> --json` — the password comes ONCE, inside `connection_string` only; the event's `secrets` field lists what to mask. One free shared database per organization. |
| 2. Connect it to the project | agent | `npx layero@latest db connect <database> --project <project>` — the project gets the connection string and the Data API address and public key in its build. |
| 3. Data API | agent | `npx layero@latest data enable --db <database>` — everything stays closed until access is granted. |
| 4. Tables, RLS, grants | agent | `npx layero@latest db sql <database> -c "<sql>"` — a script of several statements runs as one transaction. |
| 5. Sign-in | **person** | Dashboard: Databases → the database → «Авторизация» → «Включить авторизацию». Neither the CLI nor MCP enables it: ask the person and wait. |
| 6. Files | **person** | Dashboard: Databases → the database → «Файлы» → «Включить файлы». |
| 7. Keys for local development | agent | `npx layero@latest data env --write` writes the address and the public key into `.env.local`. |

Ask the person for steps 5 and 6 up front, before you write code that depends
on them: `auth.uid()` and the `auth` schema appear only after sign-in is
enabled (`schema "auth" does not exist` means exactly that).

## Roles — as in Supabase

`anon`, `authenticated` and `service_role` exist in every Layero database, so
migrations and tutorials work as written:

```sql
create table public.notes (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid(),
  body text not null
);
alter table public.notes enable row level security;
create policy "own notes" on public.notes for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on public.notes to authenticated;
```

Differences from Supabase you must account for:

- **No default grants.** A new table is closed over HTTP until you `GRANT` it
  (or run `npx layero@latest data grant public.notes --get user --post user`).
  Without a grant the API answers `401`/`403` with code `42501` and a `hint`
  saying how to open it — that is a missing grant, not a missing table.
  `404 unknown_table` means the table really does not exist.
- **The signed-in role also gets what is open to `anon`.** A `to anon` policy
  applies to signed-in users too.
- **`service_role` does not bypass RLS.** The secret key sees rows only
  through policies `to service_role` (add `using (true)` if the server must
  see everything).
- **Email confirmation is on** for newly enabled sign-in, as in Supabase:
  `signUp` returns no session until the link in the email is followed. The
  person can switch it off in «Авторизация» → «Подтверждать почту».

## Client

```js
import { createClient } from "@supabase/supabase-js";

export const db = createClient(
  import.meta.env.VITE_LAYERO_DATA_URL, // https://data.layero.ru/<database>
  import.meta.env.VITE_LAYERO_DATA_KEY, // pk_live_… — public, safe in the bundle
);
```

Only the public key `pk_live_…` goes to the browser; the secret `sk_live_…`
lives on the server.

## Limits per database (Free / Pro)

Requests per day 50,000 / 1,000,000 (then `429 quota_exceeded` until 00:00
UTC); sign-in users 10,000 / 100,000 (then new sign-ups are refused); file
size 50 MB; file storage 1 GB / 100 GB.

## MCP

`data_api_status`, `data_api_methods`, `data_api_grant`, `data_api_keys`,
`data_api_origins`, `data_api_probe` read and change access to an enabled
Data API. Creating a database, SQL and enabling the API go through the CLI
(steps 1–4); sign-in and files — through the person (steps 5–6).
`data_api_grant`, key changes and origins need the person's explicit consent.
