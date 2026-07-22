🎉 openEO API 1.3.0 released — [read the release notes →](#)

🌍 v1.3.0 now available

# Open- Standard for *Earth Observation Analysis*

**The openEO API** allows users to connect to Earth observation cloud back-ends in a simple and unified way.

[Get Started →](documentation/cookbook.llms.md)

100+

EO Collections

100+

Processes

8+

Backends

What is openEO

## One API. Any cloud. Any language.

Whether you're using Python, R , JavaScript or Julia - **openEO** lets you write your analysis once and run it on any compatible back-end. No vendor lock-in. No rewriting code.

✓

**Standardised processes** Use the same process names across different openEO back-ends

✓

**Datacube concept** Work with spatiotemporal datacubes natively

✓

**Reusable** Share and reuse EO workflows as processes

✓

**Open source** Apache 2.0: inspect, extend, contribute

s

example.py

copy

import openeo \# Connect to any openEO back-end conn = openeo.connect("BACKEND_URL") conn.authenticate_oidc() \# Load Sentinel-2 data as a datacube cube = conn.load_collection( "SENTINEL2_L2A", spatial_extent={"west": 4.0, "east": 4.5, "south": 51.0, "north": 51.5}, temporal_extent=\["2024-06-01", "2024-08-31"\], bands=\["B04", "B08"\] ) \# Compute NDVI ndvi = cube.ndvi(nir="B08", red="B04") ndvi.download("ndvi.nc")

> **CAUTION:**
>
> openEO is not to be confused with independant services that implement the specifications such as [openEO Platform](https://openeo.cloud/) or [CDSE](https://dataspace.copernicus.eu/). For a list of services built on top of openEO, please visit the [openEO Hub](https://hub.openeo.org/).

With openEO

## Are you interested in...

openEO can be used to process and analyze Earth observation data from diverse sources in a unified and efficient manner.

📖

### Downloading RGB image

Learn how to download and visualize RGB images from Earth observation data.

→ docs_light.html

🔧

### Performing Band Math

Perform mathematical operations on different spectral bands to derive new insights from Earth observation data.

→ evi calculation

🐍

### Bringing your own functions

Define and use your own functions to process Earth observation data within openEO workflows.

→ User-Defined-Function

📊

### Share EO workflow as Service

Deploy and manage your Earth observation workflows as a service, enabling automated processing and analysis.

→ User-defined-process

⚡

### Large-scale Processing

Process and analyze large volumes of Earth observation data efficiently using openEO's scalable infrastructure.

→ Scalability

🗺️

### Using Random Forest

Apply machine learning algorithms like Random Forest to classify and analyze Earth observation data.

→ Random Forest guide

Get started

## Choose your path

New to openEO? Start with a guide for your preferred language or tool.

📖

### Concepts & Glossary

Understand datacubes, processes, UDFs, and the openEO data model before writing any code.

→ docs_light.html

🔧

### Cookbook

Get started with practical examples and step-by-step guides to use openEO effectively for a specific usecase.

→ Step-by-step guide

🔧

### Built-in openEO Processes

Learn how to use different openEO processes to analyze Earth observation data efficiently using either 🐍 Python, 📊 R or ⚡ JavaScript clients.

→ software list

🗺️

### QGIS Plugin

Access openEO back-ends directly from QGIS with a graphical interface to visualize openEO outputs.

→ QGIS guide

🔧

### For Developers

Build a back-end or client library. API reference, profiles, and implementation guidelines.

→ developer docs

Latest news

## What’s new

| Date | Title | Author |
|----|----|----|
| May 14, 2026 | [OGC publishes openEO as a new Community Standard](news/2026-05-14-openeo-is-an-ogc-community-standard.llms.md) | Matthias Mohr |
| Feb 3, 2026 | [openEO API 1.3.0 and openEO Processes 2.0.0 RC2 released](news/2026-02-03-new-openeo-versions-130-200rc2.llms.md) | Matthias Mohr |
| Dec 22, 2025 | [New openEO QGIS plugin has been released](news/2025-12-22-new-qgis-plugin.llms.md) | Matthias Mohr, Caro Niebl |

![](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdib3g9IjAgMCAyMiAyMiIgZmlsbD0ibm9uZSIgc3R5bGU9InZlcnRpY2FsLWFsaWduOm1pZGRsZTttYXJnaW4tcmlnaHQ6NnB4OyI+PGNpcmNsZSBjeD0iMTEiIGN5PSIxMSIgcj0iMTAiIHN0cm9rZT0iIzdkZDllOCIgc3Ryb2tlLXdpZHRoPSIxLjUiPjwvY2lyY2xlPjxwYXRoIGQ9Ik02IDExIFExMSA1IDE2IDExIFExMSAxNyA2IDExWiIgZmlsbD0iIzdkZDllOCIgb3BhY2l0eT0iMC43IiAvPjwvc3ZnPg==) openEO

The project maintains the API and process specifications, and an open-source ecosystem with clients and server implementations.

#### Documentation

- [Introduction](#)
- [Datacubes](#)
- [Processes](#)
- [Cookbook](#)
- [Authentication](#)

#### Clients

- [CRAN / R](https://cran.r-project.org/package=openeo)
- [npm / JS](https://www.npmjs.com/search?q=%40openeo%2F)
- [PyPI / Python](https://pypi.org/project/openeo/)
- [Conda Forge](https://anaconda.org/conda-forge/openeo)
- [Julia](https://github.com/Open-EO/openeo-julia-client)
- [QGIS](https://plugins.qgis.org/plugins/openeo_plugin/)

© 2026 openEO — Apache 2.0 License  ·  Built with Quarto
