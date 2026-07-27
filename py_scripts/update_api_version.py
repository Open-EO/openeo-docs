import requests
from pathlib import Path

release = requests.get(
    "https://api.github.com/repos/Open-EO/openeo-api/releases/latest"
).json()

version = release["tag_name"].lstrip("v")
url = release["html_url"]

hub_backends = requests.get(
    "https://hub.openeo.org/api/backends?details=grouped"
).json()
documented_processes = requests.get(
    "https://openeo.org/documentation/1.0/processes.json"
).json()

# Count unique backend service URLs to avoid double counting multiple API versions
# of the same backend.
backend_count = len(
    {
        backend.get("baseUrl") or backend.get("backendUrl")
        for group in hub_backends
        for backend in group.get("backends", [])
        if backend.get("baseUrl") or backend.get("backendUrl")
    }
)

# Count documented processes from the official openEO process definitions.
process_count = len(documented_processes)

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