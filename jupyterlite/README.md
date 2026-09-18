# openEO JupyterLite

This directory is the source for the JupyterLite site bundled into the documentation deployment.

During the GitHub Pages build, the whole `openeo-community-examples/python` submodule folder is copied into `jupyterlite/files/notebooks/` and JupyterLite is built into `_site/jupyterlite/`.

The site is hosted at `https://open-eo.github.io/openeo-docs/jupyterlite/`.
It runs entirely in the visitor's browser. All bundled notebooks are provided as a lightweight showcase. Their helper files, datasets, and Python dependencies are intentionally not bundled. Users can install browser-compatible packages interactively when experimenting, but cloud-authenticated workflows are not expected to run end-to-end in JupyterLite.