# openEO documentation

Source repository for the [openEO documentation site](https://open-eo.github.io/openeo-docs/). The site documents the openEO API, processes, clients, backends, examples, and project news.

The website is built with [Quarto](https://quarto.org/) and published through GitHub Pages.

## Prerequisites

- [Quarto](https://quarto.org/docs/get-started/)
- Python 3.11 or later (GitHub Actions uses Python 3.11)
- Git, including submodule support

## Get started

Clone the repository together with its example-notebook submodule:

```powershell
git clone --recurse-submodules https://github.com/Open-EO/openeo-docs.git
cd openeo-docs
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the repository was already cloned without submodules, initialise them with:

```powershell
git submodule update --init --recursive
```

### Preview locally

Run:

```powershell
quarto preview
```

The local preview is configured to use [http://localhost:5555](http://localhost:5555). Quarto watches the source files and rebuilds the pages when they change. Use `Ctrl+C` to stop it.

To produce a complete local build without the preview server, run:

```powershell
quarto render
```

The generated website is written to `_site/`, which is not committed.

## Content and structure

- `index.qmd` – homepage
- `documentation/` – user documentation and cookbook content
- `news/`, `events/`, and `meetings.qmd` – project communication
- `custom.css` and `custom.html` – shared presentation and browser behaviour
- `_quarto.yml` – Quarto site configuration, navigation, rendering rules, and pre-render hooks
- `news/images/` – shared image assets, including the navbar logo

Use `.qmd` files for new Quarto content. Quarto resolves relative links and images from the location of the source file.

## Client examples submodule

`client_examples/openeo-community-examples` is a Git submodule pointing to the [openEO community examples](https://github.com/Open-EO/openeo-community-examples) repository. It contains notebooks and supporting material used by the documentation.

The submodule is deliberately excluded from Quarto's normal render input. Update an example in its own repository, then update the submodule pointer in this repository:

```powershell
cd client_examples/openeo-community-examples
git pull origin main
cd ../..
git add client_examples/openeo-community-examples
```

Commit the updated pointer together with any documentation links that use the example.

## Generated version and Hub data

Before every Quarto render, `py_scripts/update_api_version.py` fetches:

- the latest [openEO API release](https://github.com/Open-EO/openeo-api/releases);
- the backend count from the [openEO Hub](https://hub.openeo.org/); and
- the process count from the official openEO process catalogue.

It writes the generated values to `_variables.yml` and `_data/_variables.yml`. These values are used by the site, for example on the homepage. A render therefore needs internet access to these services.

## Image checking

`py_scripts/check_images.py` runs before Quarto renders. It checks local image references in Quarto/Markdown sources, notebooks, and CSS and prints warnings for missing files. External URLs and data URLs are skipped.

Run it directly with:

```powershell
python py_scripts/check_images.py
```

Use strict mode when you want missing local images to fail the command:

```powershell
python py_scripts/check_images.py --strict
# or
$env:IMAGE_CHECK_STRICT = '1'
python py_scripts/check_images.py
```

## JupyterLite showcase

The GitHub Pages workflows build an openEO-hosted JupyterLite site at:

`https://open-eo.github.io/openeo-docs/jupyterlite/`

The current showcase bundles the Random Forest training notebook only. It is intended for exploring the notebook interface; helper files, datasets, and scientific dependencies are not preinstalled. See [jupyterlite/README.md](jupyterlite/README.md) for details.

## Publishing

GitHub Actions handles site publication:

- pushes to `main` render Quarto, build JupyterLite, and deploy the site to GitHub Pages;
- pushes to `staging` render and archive a staging build under the `gh-pages` branch; and
- pull requests receive archived previews under `gh-pages/previews/`.

The relevant workflow files are in `.github/workflows/`. Do not commit `_site/` or generated JupyterLite content.

## Contributing

Keep changes focused, use relative links for repository content, and run `quarto preview` or `quarto render` before opening a pull request. If you change an image reference, run the image checker and ensure it points to an existing local asset.
