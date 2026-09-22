"""Validate required fields in the public project catalog."""
from __future__ import annotations
import sys
import yaml

def validate(path: str) -> list[str]:
    with open(path, encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    errors = []
    for index, item in enumerate(payload.get("projects", []), start=1):
        for field in ("name", "url", "themes"):
            if not item.get(field):
                errors.append(f"project {index}: missing {field}")
        if item.get("url") and not item["url"].startswith("https://github.com/hrix7/"):
            errors.append(f"project {index}: unexpected URL")
    return errors

if __name__ == "__main__":
    issues = validate(sys.argv[1] if len(sys.argv) > 1 else "projects.yaml")
    print("\n".join(issues) if issues else "Catalog is valid.")
    raise SystemExit(bool(issues))
