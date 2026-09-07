"""Generate live backend/process support data for the documentation filter UI."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

HUB_URL = "https://hub.openeo.org/api/backends?details=grouped"
TIMEOUT_SECONDS = 5
USER_AGENT = "openeo-docs-process-support-generator"

# Stable identifiers used by the documentation UI. New Hub groups are included
# automatically with a slug derived from their name.
GROUP_TAGS = {
    "Terrascope": "vito",
    "Copernicus Data Space Ecosystem": "cdse",
    "Copernicus Data Space Ecosystem Federation": "federation",
    "EURAC": "eurac",
    "EODC": "eodc",
    "Google Earth Engine": "gee",
    "rasdaman": "rasdaman",
    "EO4EU Platform": "eo4eu",
}


def tag_for_group(group: str) -> str:
    return GROUP_TAGS.get(group, "".join(c.lower() if c.isalnum() else "-" for c in group).strip("-"))


def version_key(value: str) -> tuple[int, ...]:
    return tuple(int(part) if part.isdigit() else 0 for part in value.split("."))


def get_json(url: str) -> Any | None:
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"Warning: failed to fetch {url}: {exc}")
        return None


def process_ids(payload: Any) -> set[str]:
    if not isinstance(payload, dict):
        return set()
    processes = payload.get("processes", [])
    if not isinstance(processes, list):
        return set()
    return {str(process["id"]) for process in processes if isinstance(process, dict) and process.get("id")}


def process_urls(service: str, api_version: str) -> list[str]:
    """Return the versioned process endpoint advertised by the Hub service URL."""
    service = service.rstrip("/")
    if service.endswith("/openeo"):
        return [f"{service}/{api_version}/processes"]
    return [f"{service}/openeo/{api_version}/processes"]


def select_backends(grouped: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Use only the newest API version of each Hub service."""
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for group in grouped:
        for backend in group.get("backends", []):
            service = backend.get("service")
            name = backend.get("group")
            if not isinstance(service, str) or not isinstance(name, str):
                continue
            key = (name, service)
            if key not in selected or version_key(str(backend.get("api_version", "0"))) > version_key(str(selected[key].get("api_version", "0"))):
                selected[key] = backend
    return list(selected.values())


def main() -> None:
    grouped = get_json(HUB_URL)
    if not isinstance(grouped, list):
        raise SystemExit("Unable to retrieve the openEO Hub backend listing.")

    backends: dict[str, dict[str, Any]] = {}
    support: dict[str, list[str]] = {}
    for backend in select_backends(grouped):
        group = str(backend["group"])
        tag = tag_for_group(group)
        service = str(backend["service"])
        api_version = str(backend.get("api_version", ""))

        ids: set[str] = set()
        source = "hub-cache"
        for url in process_urls(service, api_version):
            ids = process_ids(get_json(url))
            if ids:
                source = "live"
                break
        if not ids:
            ids = {str(item["id"]) for item in backend.get("processes", []) if isinstance(item, dict) and item.get("id")}

        backends[tag] = {
            "label": group,
            "service": service,
            "api_version": api_version,
            "source": source,
        }
        for process_id in ids:
            support.setdefault(process_id, []).append(tag)

    output = {
        "generated_at": datetime.now(UTC).isoformat(),
        "backends": backends,
        "processes": {process_id: sorted(tags) for process_id, tags in sorted(support.items())},
    }
    target = Path("_data/backend_process_support.json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Generated process support for {len(backends)} backends and {len(support)} processes.")


if __name__ == "__main__":
    main()