# Glossary

The openEO glossary provides definitions and explanations for key terms used throughout the openEO documentation.

## General terms

- **EO**: Earth Observation
- **API**: Application Programming Interface ([wikipedia](https://en.wikipedia.org/wiki/Application_programming_interface)), a (standardised) communication protocol, for example, between a client application and a backend service
- **client**: Software tool, framework or environment that an end-user directly interacts with. For example: a Jupyter notebook, a Python script/application, an RStudio session, a JavaScript-based web app, etc.
- **(cloud) backend**: server; computer infrastructure (one or more physical computers or virtual machines) used for storing EO data and processing it
- **big Earth observation cloud backend**: server infrastructure where industry and researchers analyse large amounts of EO data

## Processes

A **process** is an operation that performs a specific task on a set of parameters and returns a result. An example is computing a statistical operation, such as mean or median, on selected EO data. A process is similar to a function or method in programming languages.

A **pre-defined process** is a process provided by the *back-end*, typically [one of the processes centrally defined by openeo.org](https://processes.openeo.org/).

A **user-defined process** is a process defined by the *user*. It can be part of another process graph directly or stored as a custom process on the backend Internally, it is a *process graph* with optional additional metadata.

A **process graph** chains specific process calls from the set of predefined and user-defined processes. A process graph itself is a (user-defined) process again. Similar to scripts in programming, process graphs organise and automate the execution of one or more processes that could otherwise be executed individually.

Process graphs can be parameterised by using placeholders (parameters) instead of actual values at various points in the process graph. This turns them into so-called user-defined processes that can be reused flexibly in other process graphs. It also simplifies sharing and reusing openEO workflows across users.

## EO data (Collections)

In the Earth Observation domain, different terms are used to describe EO data(sets). Within openEO, a **granule** (sometimes also called *item* or *asset* in the specification) typically refers to a limited area and a single overpass leading to a very short observation period (seconds) or a temporal aggregation of such data (e.g. for 16-day MODIS composites). A **collection** is a sequence of granules sharing the same product specification. It typically corresponds to the series of products derived from data acquired by a sensor on board a satellite that operates in the same mode.

The [CEOS OpenSearch Best Practice Document v1.2](http://ceos.org/ourwork/workinggroups/wgiss/access/opensearch/) lists the following synonyms used by other organizations:

- **granule**: dataset (ESA, ISO 19115), granule (NASA), product (ESA, CNES), scene (JAXA)
- **collection**: dataset series (ESA, ISO 19115), collection (CNES, NASA), dataset (JAXA), product (JAXA)

In openEO, a backend provides a set of collections for processing. All collections can be requested via a client and described using the [STAC (SpatioTemporal Asset Catalogue) metadata specification](https://github.com/radiantearth/stac-spec) as STAC collections. A user can load (a subset of) a collection using a special process, which returns a (spatial) datacube. All further processing is then applied to the datacube on the backend

## Spatial datacubes

A spatiotemporal datacube is a multidimensional array with one or more spatial or temporal dimensions. In the EO domain, it is common to be implicit about the temporal dimension and refer to them as spatial datacubes in short. Special cases are raster and [vector datacubes](https://r-spatial.org/r/2022/09/12/vdc.html). Learn more about datacubes in the [datacube documentation](https://openeo.org/documentation/1.0/datacubes.html).

## Vector data

In general, **vector data** represent specific things (also called “features”) in a space, e.g. on the surface of the Earth. It comprises individual points, represented as coordinate pairs, that indicate physical locations in the world.  These points can be joined, in a particular order, to form lines or joined into closed areas to form polygons.

A **coordinate** represents a specific point in space.

A **feature** is a thing that usually has a geometry (e.g. the outline of an agricultural field, a forest or an urban area) and it may have additional properties assigned (e.g. a name, a colour, or a population). In rare cases, features may lack geometry, often referred to as an “empty geometry”.

**Geometries** consist of one or more coordinates that may be connected to form a specific type of geometry; e.g., two points can be connected to form a straight line, and four straight lines can be connected to form a rectangle.

Commonly used types of geometries are: - Point - LineString (connected straight line pieces) - Polygon (connected straight line pieces forming a closed ring, possibly with holes - for example, a triangle or rectangle)

Furthermore, these base geometries can be grouped to form, for example, so-called “multi-point” or “multi-polygon” geometries. It’s important to note that these multi-geometries act as single entities with regard to their associated properties.

Features and geometries are specified by the OGC in the [Simple Feature Access specification](https://www.ogc.org/standards/sfa) (and ISO 19125). See the specification for more details.

## User-defined function (UDF)

The abbreviation **UDF** stands for **user-defined function**. With this concept, users can upload custom code and have it executed, e.g., for every pixel of a scene or for a particular dimension or set of dimensions, enabling custom server-side calculations.

## Data Processing modes

Processes can run in three different ways:

1.  Results can be pre-computed by creating a ***batch job***.  They are submitted to the backend, but will remain inactive until explicitly added to the processing queue. They will run only once and store results after execution. The results can be downloaded once completed. This is the only mode that allows you to get an estimate of time, volume    

2.  Processes can also be executed **on-demand** (i.e. synchronously). Results are delivered with the request itself, and no job is created. Only lightweight computations, such as previews, should be executed using this approach, as timeouts are to be expected for [long-polling HTTP requests](https://www.pubnub.com/blog/http-long-polling/).

3.  The third way of data processing in openEO is **client-side processing**. The client-side processing functionality allows testing and use openEO with its processes locally, i.e. without any connection to an openEO backend. It relies on the projects [openeo-pg-parser-networkx](https://github.com/Open-EO/openeo-pg-parser-networkx), which provides an openEO process graph parsing tool, and [openeo-processes-dask](https://github.com/Open-EO/openeo-processes-dask), which provides an Xarray and Dask implementation of most openEO processes.
