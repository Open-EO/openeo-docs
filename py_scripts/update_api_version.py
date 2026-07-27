import requests
from pathlib import Path

release = requests.get(
    "https://api.github.com/repos/Open-EO/openeo-api/releases/latest"
).json()

version = release["tag_name"].lstrip("v")
url = release["html_url"]

Path("_data").mkdir(exist_ok=True)

# Create _variables.yml in the root for Quarto to automatically load
Path("_variables.yml").write_text(
f"""# Automatically generated from GitHub API
api-version: "{version}"
api-release-url: "{url}"
"""
)
print("API VERSION SCRIPT EXECUTED")