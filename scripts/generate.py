#!/usr/bin/env python3
"""Regenerate the public docs site from templates and the live /stats feed.

Outputs (written to repo root):
- index.html
- openapi.json
- status.json

No secrets required. The /stats endpoint is public.
"""

from __future__ import annotations

import json
import pathlib
import sys
import urllib.error
import urllib.request

STATS_URL = "https://mgkjwvuvndqruhfpgzwa.supabase.co/functions/v1/stats"
ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"


def fetch_stats() -> dict:
    req = urllib.request.Request(
        STATS_URL,
        headers={"user-agent": "moi-docs-generator/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"stats endpoint returned {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def render(template_path: pathlib.Path, replacements: dict[str, str]) -> str:
    text = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def fmt(n: int) -> str:
    return f"{n:,}"


def main() -> int:
    try:
        stats = fetch_stats()
    except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError) as e:
        print(f"ERROR: could not fetch stats: {e}", file=sys.stderr)
        return 1

    coverage = stats["coverage"]
    breakdown = stats["source_breakdown"]

    replacements = {
        "generated_at": stats["generated_at"],
        "generated_at_date": stats["generated_at"].split("T", 1)[0],
        "rule_version": stats["rule_version"],
        "companies": str(coverage["companies"]),
        "tickers": str(coverage["tickers"]),
        "simplified_names": str(coverage["simplified_names"]),
        "source_rule": str(breakdown["rule"]),
        "source_admin": str(breakdown["admin"]),
        "source_llm": str(breakdown["llm"]),
        "companies_fmt": fmt(coverage["companies"]),
        "tickers_fmt": fmt(coverage["tickers"]),
        "rule_fmt": fmt(breakdown["rule"]),
        "admin_fmt": fmt(breakdown["admin"]),
    }

    (ROOT / "index.html").write_text(
        render(TEMPLATES / "index.html.tmpl", replacements),
        encoding="utf-8",
    )
    (ROOT / "openapi.json").write_text(
        render(TEMPLATES / "openapi.json.tmpl", replacements),
        encoding="utf-8",
    )
    # status.json is the raw stats payload, pretty printed.
    (ROOT / "status.json").write_text(
        json.dumps(stats, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Regenerated index.html, openapi.json, status.json")
    print(
        f"  companies={coverage['companies']} "
        f"tickers={coverage['tickers']} "
        f"rule={breakdown['rule']} "
        f"admin={breakdown['admin']} "
        f"llm={breakdown['llm']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
