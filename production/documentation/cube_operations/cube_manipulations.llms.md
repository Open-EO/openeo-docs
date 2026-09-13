# Cube Manipulations

Cube-manipulation processes change a cube’s structure without changing the scientific question: combine compatible cubes, add derived bands, and make dimensions easier to work with.

VITO

EODC

CDSE

Sentinel Hub

> **NOTE:**
>
> The buttons on this page are a documentation aid, not a live capability registry. Use the [openEO Hub](https://hub.openeo.org/) for a cross-backend overview: open **Filters**, select a process under **Processes**, and the Hub shows only matching services. The Hub data is crawled and cached.

> **NOTE:**
>
> These are standardized processes, but a backend can implement a subset or impose compatibility rules. Check its process metadata before relying on a workflow.

## Merge cubes

`merge_cubes` combines two compatible cubes. Without an overlap resolver, the cubes must not contain overlapping labels. When they do overlap, provide a callback that defines how values are combined.

### Python

``` python
# For example: stack two non-overlapping seasonal cubes.
full_year = spring.merge_cubes(summer)
```

Use `merge_cubes` for a union of compatible data. Use `resample_cube_spatial` or `resample_cube_temporal` first when grids or time labels must be aligned.

------------------------------------------------------------------------

## Add a dimension

`add_dimension` can turn a single-band result into a labelled band in a larger workflow.

### Python

``` python
# Add a named band dimension to a single-band derived raster.
with_band = derived.add_dimension(name="NDVI", label="bands", type="bands")
```

`drop_dimension` removes a dimension only when it has one label. For other structural changes, see `flatten_dimensions` and `unflatten_dimension` in the [process reference](https://processes.openeo.org/).

## Rename dimension labels

`rename_labels` replaces labels while keeping the dimension structure unchanged.

``` python
renamed = with_band.rename_labels(dimension="bands", target=["vegetation_index"])
```

## Cube-structure process details

Each structural process is documented in its own section below. A process is documented on another operations page when its primary purpose is analysis along that dimension.

## Drop a singleton dimension

Use `drop_dimension` after a workflow produces a dimension with one label and that dimension is no longer useful in the output. It does not remove a dimension containing multiple labels.

``` python
without_singleton = cube.drop_dimension(dimension="bands")
```

## Rename a dimension

Use `rename_dimension` to make a dimension name match the vocabulary expected by a later process or output consumer. The labels and values remain unchanged.

``` python
renamed = cube.rename_dimension(dimension="bands", target="spectral")
```

## Read dimension labels

Use `dimension_labels` when a workflow needs to inspect or pass on the labels of a dimension, for example band names or temporal labels.

``` python
labels = cube.dimension_labels(dimension="bands")
```

## Filter dimension labels

Use `filter_labels` to select a subset of labels such as specific bands, dates, or categories while keeping the other cube dimensions intact.

``` python
selected = cube.filter_labels(dimension="bands", condition=lambda label: label != "QA")
```

## Flatten dimensions

Use `flatten_dimensions` when a downstream model expects a single feature axis instead of separate spatial or categorical dimensions. Keep the original labels if you may need to reverse the operation.

``` python
flattened = cube.flatten_dimensions(dimension_names=["x", "y"], target_dimension="pixels")
```

## Unflatten a dimension

Use `unflatten_dimension` to restore the dimensions represented by a flattened axis, for example after a model or export step that required one feature dimension.

``` python
unflattened = flattened.unflatten_dimension(dimension="pixels", target_dimensions=["x", "y"])
```
