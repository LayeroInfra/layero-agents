#!/usr/bin/env python3
"""Генерирует адаптеры из канона. Единственный способ менять plugins/*,
server.json, .mcp.json, маркетплейсы и блок установки в README.

Канон: skills/layero/, mcp.json, agents-install.json, assets/logo.svg,
README.md вне маркеров <!-- install:start --> … <!-- install:end -->.

Запуск: python3 build-adapters.py [--out DIR]
Без --out пишет в корень репозитория; с --out — в указанную папку
(так работает гейт check-surfaces.py).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

VERSION = "2.1.1"
MCP_NAME = "layero"
OWNER = {"name": "Layero", "url": "https://layero.ru"}
HOMEPAGE = "https://docs.layero.ru/agents/"
REPOSITORY = "https://github.com/LayeroInfra/layero-agents"
KEYWORDS = ["deploy", "deployment", "hosting", "static-site", "ssr", "russia", "mcp", "data-api"]

DESCRIPTION_RU = (
    "Деплой и эксплуатация сайтов на Layero — хостинге с серверами сборки в России: "
    "деплои, домены, переменные окружения, Data API. Навык и MCP-сервер."
)
DESCRIPTION_EN = (
    "Deploy and operate sites on Layero — hosting with build servers in Russia: "
    "domains, env, Data API."
)
MARKETPLACE_DESCRIPTION_RU = (
    "Официальный маркетплейс Layero. Layero — платформа хостинга и деплоя с серверами "
    "сборки в России: репозиторий или папка → сайт, домены, превью-ветки, Data API."
)
MARKETPLACE_DESCRIPTION_EN = (
    "Official Layero marketplace: deploy and operate sites on hosting with build "
    "servers in Russia, straight from the editor."
)
TOKEN_HEADER_DESCRIPTION = (
    "Layero token for CI and headless clients, issued at https://app.layero.ru/settings/cli "
    "or with `npx layero@latest token create`. Optional: interactive clients sign in "
    "through OAuth."
)

# Подписи инструментов для карточки Cursor (_meta.ideToolTitles).
TOOL_TITLES = {
    "whoami": "Who Am I",
    "my_projects": "My Projects",
    "list_sources": "List Sources",
    "import_repo": "Import Repository",
    "list_environments": "List Environments",
    "project_create": "Create Project",
    "site_status": "Site Status",
    "env_vars": "Environment Variables",
    "connect_analytics": "Connect Analytics",
    "site_analytics": "Site Analytics",
    "check_performance": "Check Performance",
    "connect_domain": "Connect Domain",
    "check_domain": "Check Domain",
    "list_domains": "List Domains",
    "read_site": "Read Site",
    "site_screenshot": "Site Screenshot",
    "site_issues": "Site Issues",
    "refactor_site": "Refactor Site",
    "check_copy": "Check Copy",
    "list_deploys": "List Deploys",
    "rollback": "Rollback",
    "retry_deploy": "Retry Deploy",
    "cancel_deploy": "Cancel Deploy",
    "deploy_logs": "Deploy Logs",
    "diagnose_deploy": "Diagnose Deploy",
    "publish_site": "Publish Site",
    "publish_landing": "Publish Site (deprecated alias)",
    "data_api_status": "Data API Status",
    "data_api_methods": "Data API Methods",
    "data_api_grant": "Data API Grant",
    "data_api_keys": "Data API Keys",
    "data_api_origins": "Data API Origins",
    "data_api_probe": "Data API Probe",
}

CURSOR_RULE_FRONTMATTER = """---
description: "Deploying to Layero and operating sites hosted there: CLI JSON events, MCP tools, layero.json, git providers"
globs: package.json, vite.config.*, next.config.*, astro.config.*, nuxt.config.*, svelte.config.*, layero.json, **/.layero/project.json
alwaysApply: false
---
"""

INSTALL_START = "<!-- install:start -->"
INSTALL_END = "<!-- install:end -->"


def dump(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_canon():
    skill_dir = ROOT / "skills" / "layero"
    skill_files = {
        p.relative_to(skill_dir).as_posix(): p.read_bytes()
        for p in sorted(skill_dir.rglob("*")) if p.is_file()
    }
    if "SKILL.md" not in skill_files:
        sys.exit("нет skills/layero/SKILL.md")
    return {
        "mcp": json.loads((ROOT / "mcp.json").read_text(encoding="utf-8")),
        "install": json.loads((ROOT / "agents-install.json").read_text(encoding="utf-8")),
        "skill": skill_files,
        "logo": (ROOT / "assets" / "logo.svg").read_bytes(),
        "readme": (ROOT / "README.md").read_text(encoding="utf-8"),
    }


def mcp_with_token(mcp: dict) -> dict:
    server = dict(mcp["mcpServers"][MCP_NAME])
    server["headers"] = {"Authorization": "Bearer ${LAYERO_TOKEN}"}
    return {"mcpServers": {MCP_NAME: server}}


def mcp_for_cursor(mcp: dict) -> dict:
    # Cursor не раскрывает ${VAR} — нераскрытая строка ушла бы на сервер как
    # «Invalid token». Поэтому без заголовка; вход — OAuth или подсказка сервера.
    server = dict(mcp["mcpServers"][MCP_NAME])
    server["_meta"] = {"ideToolIconPath": "./assets/logo.svg", "ideToolTitles": TOOL_TITLES}
    return {"mcpServers": {MCP_NAME: server}}


def skill_body(skill_md: bytes) -> str:
    text = skill_md.decode("utf-8")
    m = re.match(r"---\n.*?\n---\n", text, re.S)
    if not m:
        sys.exit("SKILL.md без frontmatter")
    return text[m.end():].lstrip("\n")


def cursor_rule(skill_md: bytes) -> bytes:
    body = skill_body(skill_md)
    body = body.replace("](references/", "](../skills/layero/references/")
    return (CURSOR_RULE_FRONTMATTER + body).encode("utf-8")


def install_block(install: dict) -> str:
    rows = ["| Клиент | Команда |", "|---|---|"]
    for c in install["clients"]:
        cmd = f"`{c['command']}`"
        if c.get("deeplink"):
            cmd += f" · [одной кнопкой]({c['deeplink']})"
        rows.append(f"| **{c['label']}** | {cmd} |")
    ci = install["ci"]
    lines = [
        INSTALL_START,
        f"MCP: `{install['mcp']['url']}` (сервер `{install['mcp']['name']}`, транспорт "
        f"{install['mcp']['transport']}) · навык: `{install['skills_repo']}`",
        "",
        *rows,
        "",
        f"CI и бездисплейные среды — токен в `{ci['env']}`:",
        "",
        "```bash",
        ci["command"],
        "```",
        INSTALL_END,
    ]
    return "\n".join(lines)


def readme_with_block(readme: str, install: dict) -> bytes:
    start, end = readme.find(INSTALL_START), readme.find(INSTALL_END)
    if start < 0 or end < 0 or end < start:
        sys.exit("README.md: нет пары маркеров install:start / install:end")
    end += len(INSTALL_END)
    return (readme[:start] + install_block(install) + readme[end:]).encode("utf-8")


def generate() -> dict[str, bytes]:
    canon = read_canon()
    mcp, install, skill = canon["mcp"], canon["install"], canon["skill"]
    url = mcp["mcpServers"][MCP_NAME]["url"]
    if url != install["mcp"]["url"]:
        sys.exit(f"mcp.json и agents-install.json расходятся в адресе: {url} ≠ {install['mcp']['url']}")
    if len(DESCRIPTION_EN) > 100:
        sys.exit(f"description для server.json длиннее 100 символов: {len(DESCRIPTION_EN)}")

    out: dict[str, bytes] = {}

    plugin_meta = {
        "author": OWNER, "homepage": HOMEPAGE, "repository": REPOSITORY,
        "license": "MIT", "keywords": KEYWORDS,
    }

    # Claude Code
    out[".claude-plugin/marketplace.json"] = dump({
        "name": "layero",
        "owner": OWNER,
        "metadata": {"description": MARKETPLACE_DESCRIPTION_RU, "version": VERSION},
        "plugins": [{
            "name": "layero", "source": "./plugins/layero",
            "description": DESCRIPTION_RU, "version": VERSION, **plugin_meta,
        }],
    })
    out["plugins/layero/.claude-plugin/plugin.json"] = dump({
        "name": "layero", "description": DESCRIPTION_RU, "version": VERSION, **plugin_meta,
    })
    out["plugins/layero/.mcp.json"] = dump(mcp_with_token(mcp))
    for rel, data in skill.items():
        out[f"plugins/layero/skills/layero/{rel}"] = data

    # Cursor
    out[".cursor-plugin/marketplace.json"] = dump({
        "name": "layero",
        "owner": OWNER,
        "metadata": {"description": MARKETPLACE_DESCRIPTION_EN, "version": VERSION},
        "plugins": [{
            "name": "layero", "source": "./plugins/layero-cursor", "description": DESCRIPTION_EN,
        }],
    })
    out["plugins/layero-cursor/.cursor-plugin/plugin.json"] = dump({
        "name": "layero", "displayName": "Layero", "version": VERSION,
        "description": DESCRIPTION_EN, **plugin_meta, "logo": "assets/logo.svg",
    })
    out["plugins/layero-cursor/mcp.json"] = dump(mcp_for_cursor(mcp))
    for rel, data in skill.items():
        out[f"plugins/layero-cursor/skills/layero/{rel}"] = data
    out["plugins/layero-cursor/rules/layero.mdc"] = cursor_rule(skill["SKILL.md"])
    out["plugins/layero-cursor/assets/logo.svg"] = canon["logo"]

    # Реестр MCP
    out["server.json"] = dump({
        "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
        "name": "ru.layero/layero",
        "title": "Layero",
        "description": DESCRIPTION_EN,
        "websiteUrl": HOMEPAGE,
        "repository": {"url": REPOSITORY, "source": "github"},
        "version": VERSION,
        "remotes": [{
            "type": "streamable-http",
            "url": url,
            "headers": [{
                "name": "Authorization",
                "description": TOKEN_HEADER_DESCRIPTION,
                "isRequired": False,
                "isSecret": True,
                "placeholder": "Bearer layero_ci_...",
            }],
        }],
    })

    # Корень: Claude Code читает .mcp.json при клонировании
    out[".mcp.json"] = dump(mcp_with_token(mcp))
    out["README.md"] = readme_with_block(canon["readme"], install)
    return out


# Папки, содержимое которых целиком генерируется: лишние файлы в них — ошибка.
GENERATED_DIRS = (".claude-plugin", ".cursor-plugin", "plugins")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=ROOT)
    args = ap.parse_args()
    files = generate()
    for rel, data in files.items():
        path = args.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
            print(f"  → {rel}")
    print(f"сгенерировано {len(files)} файлов")


if __name__ == "__main__":
    main()
