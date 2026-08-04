import requests
from pathlib import Path

TIMEOUT_SECONDS = 20


def load_existing_variables(path: Path) -> dict:
    """Load simple key/value pairs from the generated variables file."""
    if not path.exists():
        return {}

    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        values[key.strip()] = raw_value.strip().strip('"')
    return values


def fetch_json(url: str):
    """Fetch JSON with graceful fallback for transient API failures."""
    try:
        response = requests.get(
            url,
            timeout=TIMEOUT_SECONDS,
            headers={"User-Agent": "openeo-docs-version-updater"},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"Warning: failed to fetch {url}: {exc}")
        return None


existing = load_existing_variables(Path("_variables.yml"))

release = fetch_json("https://api.github.com/repos/Open-EO/openeo-api/releases/latest")
hub_backends = fetch_json("https://hub.openeo.org/api/backends?details=grouped")
documented_processes = fetch_json("https://openeo.org/documentation/1.0/processes.json")

if isinstance(release, dict) and release.get("tag_name"):
    version = str(release["tag_name"]).lstrip("v")
else:
    version = existing.get("api-version", "unknown")
    print("Warning: GitHub release payload missing 'tag_name'; using existing api-version.")

if isinstance(release, dict) and release.get("html_url"):
    url = str(release["html_url"])
else:
    url = existing.get("api-release-url", "https://github.com/Open-EO/openeo-api/releases")
    print("Warning: GitHub release payload missing 'html_url'; using existing api-release-url.")

# Count unique backend service URLs to avoid double counting multiple API versions
# of the same backend.
backend_count = len(
    {
        backend.get("baseUrl") or backend.get("backendUrl")
        for group in (hub_backends or [])
        for backend in group.get("backends", [])
        if backend.get("baseUrl") or backend.get("backendUrl")
    }
)

# Count documented processes from the official openEO process definitions.
if isinstance(documented_processes, (list, dict)):
    process_count = len(documented_processes)
else:
    process_count = int(existing.get("hub-processes-count", "0"))
    print("Warning: process definitions unavailable; using existing hub-processes-count.")

if not hub_backends:
    backend_count = int(existing.get("hub-backends-count", "0"))
    print("Warning: backend listing unavailable; using existing hub-backends-count.")

variables_content = f"""# Automatically generated from GitHub API, openEO Hub, and openEO docs
api-version: "{version}"
api-release-url: "{url}"
hub-backends-count: "{backend_count}"
hub-processes-count: "{process_count}"
"""

Path("_data").mkdir(exist_ok=True)

# Create _variables.yml in the root for Quarto to automatically load.
Path("_variables.yml").write_text(variables_content)

# Keep a copy in _data for workflows that read variables from there.
Path("_data/_variables.yml").write_text(variables_content)
print("API VERSION SCRIPT EXECUTED")