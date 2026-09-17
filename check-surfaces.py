#!/usr/bin/env python3
"""Гейт: адаптеры совпадают с генерацией из канона.

1. Прогоняет build-adapters.py во временную папку и сравнивает каждый файл
   байт в байт с закоммиченным. Расхождение — ошибка: адаптер правили руками
   или забыли `make build`.
2. В целиком генерируемых папках (plugins/, .claude-plugin/, .cursor-plugin/)
   не должно быть файлов, которых генератор не создаёт.
3. Если рядом лежат чекауты ../frontend и ../layero-docs, их копии
   agents-install.json сверяются с каноном побайтно. Отсутствие соседа —
   пропуск с пометкой, не ошибка.

Запуск: python3 check-surfaces.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATED_DIRS = (".claude-plugin", ".cursor-plugin", "plugins")
NEIGHBOUR_COPIES = (
    ROOT.parent / "frontend" / "landing" / "agents-install.json",
    ROOT.parent / "layero-docs" / "agents-install.json",
)

failures: list[str] = []


def fail(msg: str) -> None:
    print("  ✗ " + msg)
    failures.append(msg)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="layero-agents-") as tmp:
        out = Path(tmp)
        run = subprocess.run(
            [sys.executable, str(ROOT / "build-adapters.py"), "--out", str(out)],
            capture_output=True, text=True,
        )
        if run.returncode != 0:
            print(run.stdout, run.stderr)
            fail("build-adapters.py упал")
            return report()

        generated = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
        print(f"сгенерировано {len(generated)} файлов, сверяю с репозиторием")
        for rel in sorted(generated):
            committed = ROOT / rel
            if not committed.exists():
                fail(f"нет в репозитории: {rel} — выполни `make build`")
            elif committed.read_bytes() != (out / rel).read_bytes():
                fail(f"расходится с каноном: {rel} — выполни `make build`, руками не править")

    for d in GENERATED_DIRS:
        for p in (ROOT / d).rglob("*"):
            if p.is_file() and p.relative_to(ROOT).as_posix() not in generated:
                fail(f"лишний файл в генерируемой папке: {p.relative_to(ROOT)}")

    canon = (ROOT / "agents-install.json").read_bytes()
    for copy in NEIGHBOUR_COPIES:
        if not copy.exists():
            print(f"  – пропуск: нет {copy.relative_to(ROOT.parent)}")
        elif copy.read_bytes() != canon:
            fail(f"копия расходится с каноном: {copy.relative_to(ROOT.parent)}")
        else:
            print(f"  ✓ {copy.relative_to(ROOT.parent)} совпадает с каноном")
    return report()


def report() -> int:
    if failures:
        print(f"\n{len(failures)} расхождений")
        return 1
    print("\nвсе поверхности совпадают с каноном")
    return 0


if __name__ == "__main__":
    sys.exit(main())
