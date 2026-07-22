# Using the BioPAR openEO Service

This notebook demonstrates how the BioPAR openEO service can be used to compute biophysical parameters with the Sentinel-2 Level-2A data available in the Copernicus Data Space Ecosystem (CDSE).

All processing is executed in the cloud on the Copernicus Data Space Ecosystem (CDSE) infrastructure via the openEO API, so no local data download or heavy computation is required. Therefore, if you don’t yet have an account on CDSE, please register at https://dataspace.copernicus.eu

In this notebook, you will learn how to: \* Connect to the CDSE backend \* Use the BioPAR openEO service to derive biophysical parameters \* Run EO processing workflows entirely in the cloud using openEO

Prerequisites \* A CDSE account (register at https://dataspace.copernicus.eu) \* Basic familiarity with Python and Earth Observation data

## Introduction

Before we jump into the BioPAR service, let us briefly understand what openEO is and what is meant by the BioPAR openEO service.

### What is openEO?

openEO is an open-source standard that simplifies access to and processing of Earth Observation (EO) data. Instead of downloading and processing large satellite datasets locally, openEO allows users to: \* Access EO data directly where it is stored \* Run scalable processing workflows in the cloud \* Save workflows as User-Defined Processes (UDPs) \* Reuse and reshare UDPs as services This enables faster, more reproducible, and easier-to-scale EO data analysis.

### What is BioPAR openEO service?

The BioPAR openEO service is a reusable processing component (called a User-Defined Process, or UDP) provided by VITO/Terrascope through the [Copernicus Data Space Ecosystem (CDSE)](https://marketplace-portal.dataspace.copernicus.eu/catalogue/app-details/21) and the [APEx Algorithm Catalogue](https://algorithm-catalogue.apex.esa.int/apps/biopar#biophysical-parameters). It enables on-demand computation of the following biophysical parameters: \* LAI - Leaf Area Index \* FAPAR - Fraction of Absorbed Photosynthetically Active Radiation \* FCOVER - Fraction of Vegetation Cover \* CWC - Canopy Water Content \* CCC - Canopy Chlorophyll Content

The service: \* Uses Sentinel-2 Level-2A data from CDSE \* Perform cloud masking \* Applies validated BioPAR retrieval models \* Returns ready-to-use biophysical products In this notebook, we will use this service and run it directly on the CDSE cloud infrastructure.

The only package required to run this service is the `openeo` Python client, which can be installed via pip:


    pip install openeo

``` python
import openeo
```

Next, let’s set up a connection to an openEO backend that hosts the BioPAR UDP, in this case the Copernicus Data Space Ecosystem (CDSE). You can authenticate using your credentials as shown below.

``` python
connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
```

    Authenticated using refresh token.

You can find additional information on Authentication on [this page](https://open-eo.github.io/openeo-python-client/auth.html).

### openEO workflows

Before using the BioPAR openEO service, it is useful to understand the general structure of an openEO workflow.

Most openEO workflows follow the same high-level pattern: 1. Connect to an openEO backend 2. Load collection for a specific spatial and temporal extent 3. Build a processing workflow (also called a *process graph*) using openEO processes 4. Execute the workflow on the backend

For a full introduction to these concepts, please refer to the official openEO *Getting Started* notebook:  
https://github.com/Open-EO/openeo-community-examples/blob/main/python/1.%20GettingStarted/GettingStarted.ipynb

### From workflows to services

While building workflows many times from scratch can be tedious, openEO supports the creation of reusable processing chains.

Such workflows can be encapsulated as **User-Defined Processes (UDPs)** and shared as **services**. These services: - Hide the complexity of the underlying processing workflow - Require fewer inputs from the user - Ensure consistent and reproducible results

The **BioPAR openEO service** is one such service. It encompasses a comprehensive processing workflow for deriving biophysical vegetation parameters from Sentinel-2 data.

To compute a specific product from the BioPAR service, we call the BioPAR process through an active openEO connection, which returns a datacube containing the requested data. In this case, it requires: - `biopar_type`: The type of biophysical parameter to compute (e.g., ‘FAPAR’, ‘FCOVER’, ‘LAI’, ‘CCC’, ‘CWC’). - `temporal_extent`: The time range for which the data is requested. - `spatial_extent`: The area of interest. It can be a feature collection or bounding box coordinates.

The namespace parameter references a publicly accessible JSON file that defines the process graph for the BIOPAR algorithm. This graph summarizes all the steps the service performs on Sentinel-2 data to derive the requested parameter.

``` python
# Create a processing graph from the BIOPAR process using an active openEO connection
biopar = connection.datacube_from_process(
        "biopar", 
        namespace = "https://raw.githubusercontent.com/ESA-APEx/apex_algorithms/refs/heads/main/algorithm_catalog/vito/biopar/openeo_udp/biopar.json",
        temporal_extent = ["2020-05-06", "2020-05-30"],
        spatial_extent= {"west": 5.215759, "south": 51.160296, "east": 5.405960, "north": 51.244815},
        biopar_type = 'FAPAR'
        )
```

Though the example demonstrates FAPAR computation, the same approach can be used to compute other parameters like FCOVER, LAI, CCC and CWC by changing the `biopar_type` parameter.

Now let’s proceed with the execution by simply creating a job, starting it and waiting for its completion For more information on openEO batch jobs, please refer to the [openEO documentation](https://open-eo.github.io/openeo-python-client/batch_jobs.html).

``` python
job = biopar.create_job(out_format="GTiff", title="BIOPAR_FAPAR_Job")
job.start_and_wait()
```

    0:00:00 Job 'j-2601061058334edd8f0e6c8e4aaf1012': send 'start'
    0:00:15 Job 'j-2601061058334edd8f0e6c8e4aaf1012': created (progress 0%)
    0:00:20 Job 'j-2601061058334edd8f0e6c8e4aaf1012': created (progress 0%)
    0:00:27 Job 'j-2601061058334edd8f0e6c8e4aaf1012': created (progress 0%)
    0:00:35 Job 'j-2601061058334edd8f0e6c8e4aaf1012': created (progress 0%)
    0:00:45 Job 'j-2601061058334edd8f0e6c8e4aaf1012': running (progress N/A)
    0:00:57 Job 'j-2601061058334edd8f0e6c8e4aaf1012': running (progress N/A)
    0:01:12 Job 'j-2601061058334edd8f0e6c8e4aaf1012': running (progress N/A)
    0:01:32 Job 'j-2601061058334edd8f0e6c8e4aaf1012': running (progress N/A)
    0:01:56 Job 'j-2601061058334edd8f0e6c8e4aaf1012': running (progress N/A)
    0:02:25 Job 'j-2601061058334edd8f0e6c8e4aaf1012': running (progress N/A)
    0:03:03 Job 'j-2601061058334edd8f0e6c8e4aaf1012': running (progress N/A)
    0:03:50 Job 'j-2601061058334edd8f0e6c8e4aaf1012': finished (progress 100%)

Once a batch job is finished you can get a handle to the results (which can be a single file or multiple files) and metadata with `get_results()`.

``` python
results = job.get_results()
results
```

The result metadata describes the spatio-temporal properties of the result and is in fact a valid STAC item:

``` python
results.get_metadata()
```

    {'assets': {'openEO_2020-05-07Z.tif': {'bands': [{'name': 'FAPAR'}],
       'eo:bands': [{'name': 'FAPAR'}],
       'href': 'https://s3.waw3-1.openeo.v1.dataspace.copernicus.eu/openeo-data-prod-waw4-1/batch_jobs/j-2601061058334edd8f0e6c8e4aaf1012/openEO_2020-05-07Z.tif?X-Proxy-Head-As-Get=true&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=7f7c983007e7411abc0e86b1384a92c0%2F20260106%2Fwaw4-1%2Fs3%2Faws4_request&X-Amz-Date=20260106T120104Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Security-Token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2FybiI6ImFybjpvcGVuZW93czppYW06Ojpyb2xlL29wZW5lby1kYXRhLXByb2Qtd2F3NC0xLXdvcmtzcGFjZSIsImluaXRpYWxfaXNzdWVyIjoib3BlbmVvLnByb2Qud2F3My0xLm9wZW5lby1pbnQudjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJodHRwczovL2F3cy5hbWF6b24uY29tL3RhZ3MiOnsicHJpbmNpcGFsX3RhZ3MiOnsiam9iX2lkIjpbImotMjYwMTA2MTA1ODMzNGVkZDhmMGU2YzhlNGFhZjEwMTIiXSwidXNlcl9pZCI6WyIzZTI0ZTI1MS0yZTlhLTQzOGYtOTBhOS1kNDUwMGU1NzY1NzQiXX0sInRyYW5zaXRpdmVfdGFnX2tleXMiOlsidXNlcl9pZCIsImpvYl9pZCJdfSwiaXNzIjoic3RzLndhdzMtMS5vcGVuZW8udjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJzdWIiOiJvcGVuZW8tZHJpdmVyIiwiZXhwIjoxNzY3NzQ0MDY0LCJuYmYiOjE3Njc3MDA4NjQsImlhdCI6MTc2NzcwMDg2NCwianRpIjoiMDE3OTNkZWQtZDEzZS00MmUxLWJlOWEtNzkzNjJiMjE5NTFmIiwiYWNjZXNzX2tleV9pZCI6IjdmN2M5ODMwMDdlNzQxMWFiYzBlODZiMTM4NGE5MmMwIn0.Mv84A0sQ8A-Z8EOVGl02IFv2O72x5QF9LPxHg39DUKvZ_duSluv6dwlTfzi8W4GuIyj2ticKwMqyvtRxmO8zv4l4JGC445Ug1sfpEL2f14lqHBfSSvk2oCuxV1iTsLf9_hiaiguiCMJxboKUgO6TWHXRbK6V_zPifmR_b4uveb1_Mi78vxtKeus9sK4Uhbbo8A2tJyS5MW4b3gSFpigew3QuHAm9Xfh2s8yREiGtF4mHIR2zfeYKUZuCW7owRF_wx1GMVRyWlLHn1KWMkCnjFjwQvD-ekyD1OnP5oSSOeyUWsJNvDs1RDZ3qG8zJOqAD7PmI774XZx-ExWQ3LpZX2g&X-Amz-Signature=c800c27479e9cc6f4b9f74b93f2c71326b7c99997e12aafb58039a1b511a301f',
       'proj:bbox': [654650.0, 5669980.0, 668240.0, 5679810.0],
       'proj:epsg': 32631,
       'proj:shape': [983, 1359],
       'raster:bands': [{'name': 'FAPAR',
         'statistics': {'maximum': 0.97093456983566,
          'mean': 0.44890405928468,
          'minimum': 0.00015301299572457,
          'stddev': 0.24077863860759,
          'valid_percent': 98.82}}],
       'roles': ['data'],
       'title': 'openEO_2020-05-07Z.tif',
       'type': 'image/tiff; application=geotiff'},
      'openEO_2020-05-12Z.tif': {'bands': [{'name': 'FAPAR'}],
       'eo:bands': [{'name': 'FAPAR'}],
       'href': 'https://s3.waw3-1.openeo.v1.dataspace.copernicus.eu/openeo-data-prod-waw4-1/batch_jobs/j-2601061058334edd8f0e6c8e4aaf1012/openEO_2020-05-12Z.tif?X-Proxy-Head-As-Get=true&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=d3af5f284db74ac38d18dcaef47f8124%2F20260106%2Fwaw4-1%2Fs3%2Faws4_request&X-Amz-Date=20260106T120104Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Security-Token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2FybiI6ImFybjpvcGVuZW93czppYW06Ojpyb2xlL29wZW5lby1kYXRhLXByb2Qtd2F3NC0xLXdvcmtzcGFjZSIsImluaXRpYWxfaXNzdWVyIjoib3BlbmVvLnByb2Qud2F3My0xLm9wZW5lby1pbnQudjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJodHRwczovL2F3cy5hbWF6b24uY29tL3RhZ3MiOnsicHJpbmNpcGFsX3RhZ3MiOnsiam9iX2lkIjpbImotMjYwMTA2MTA1ODMzNGVkZDhmMGU2YzhlNGFhZjEwMTIiXSwidXNlcl9pZCI6WyIzZTI0ZTI1MS0yZTlhLTQzOGYtOTBhOS1kNDUwMGU1NzY1NzQiXX0sInRyYW5zaXRpdmVfdGFnX2tleXMiOlsidXNlcl9pZCIsImpvYl9pZCJdfSwiaXNzIjoic3RzLndhdzMtMS5vcGVuZW8udjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJzdWIiOiJvcGVuZW8tZHJpdmVyIiwiZXhwIjoxNzY3NzQ0MDY0LCJuYmYiOjE3Njc3MDA4NjQsImlhdCI6MTc2NzcwMDg2NCwianRpIjoiYWM4ZGQ0YjAtNDc5Ni00ZjlkLWJlNGQtMmNhNjhlN2MzMjRhIiwiYWNjZXNzX2tleV9pZCI6ImQzYWY1ZjI4NGRiNzRhYzM4ZDE4ZGNhZWY0N2Y4MTI0In0.EM3Y9UNICAAsoQGANgdsLDO2uBiFshVbgiOGW8kd4LpE_iYy-glO_Xzl9KV2VELUpQKeILokU1L9oZUfJJjv-Ol2J0oAVTYC8HD2PJVo31dW7Y1sUClHT9Q3I7IRWhKFabZAcLn5MQamtZnoaNHtMgIOpKdOpCxpiksqhRTvFk26UqMAqIEc4WO3CAxbnvfJ8hKQSjCpjnvrFThWxfhfi4_9b_Enx6vy8WU7uCOsxexjiFa9dqlQDD6D5fMQXhtsSgdky1Lom05qPcl-4bMHA4OwTKV-_yhTmfm5A8ZKFHariEEW19Ose48b5iTSfXscqn8-DToE-ya-z5xKs8ocww&X-Amz-Signature=5b84c2fa9045baad3b5fed6da2d725fb5a2eeb9d8c5ce0243028db1059b42f83',
       'proj:bbox': [654650.0, 5669980.0, 668240.0, 5679810.0],
       'proj:epsg': 32631,
       'proj:shape': [983, 1359],
       'raster:bands': [{'name': 'FAPAR',
         'statistics': {'maximum': 0.87232047319412,
          'mean': 0.56418854149414,
          'minimum': 0.31639513373375,
          'stddev': 0.059455870588817,
          'valid_percent': 0.1106}}],
       'roles': ['data'],
       'title': 'openEO_2020-05-12Z.tif',
       'type': 'image/tiff; application=geotiff'},
      'openEO_2020-05-15Z.tif': {'bands': [{'name': 'FAPAR'}],
       'eo:bands': [{'name': 'FAPAR'}],
       'href': 'https://s3.waw3-1.openeo.v1.dataspace.copernicus.eu/openeo-data-prod-waw4-1/batch_jobs/j-2601061058334edd8f0e6c8e4aaf1012/openEO_2020-05-15Z.tif?X-Proxy-Head-As-Get=true&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=6fd78408b0d948e399897a757662db71%2F20260106%2Fwaw4-1%2Fs3%2Faws4_request&X-Amz-Date=20260106T120103Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Security-Token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2FybiI6ImFybjpvcGVuZW93czppYW06Ojpyb2xlL29wZW5lby1kYXRhLXByb2Qtd2F3NC0xLXdvcmtzcGFjZSIsImluaXRpYWxfaXNzdWVyIjoib3BlbmVvLnByb2Qud2F3My0xLm9wZW5lby1pbnQudjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJodHRwczovL2F3cy5hbWF6b24uY29tL3RhZ3MiOnsicHJpbmNpcGFsX3RhZ3MiOnsiam9iX2lkIjpbImotMjYwMTA2MTA1ODMzNGVkZDhmMGU2YzhlNGFhZjEwMTIiXSwidXNlcl9pZCI6WyIzZTI0ZTI1MS0yZTlhLTQzOGYtOTBhOS1kNDUwMGU1NzY1NzQiXX0sInRyYW5zaXRpdmVfdGFnX2tleXMiOlsidXNlcl9pZCIsImpvYl9pZCJdfSwiaXNzIjoic3RzLndhdzMtMS5vcGVuZW8udjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJzdWIiOiJvcGVuZW8tZHJpdmVyIiwiZXhwIjoxNzY3NzQ0MDYzLCJuYmYiOjE3Njc3MDA4NjMsImlhdCI6MTc2NzcwMDg2MywianRpIjoiNTM4MzQyMGQtODQ1ZS00N2ZjLThiZDktNjQ0MmViZmU5MTBkIiwiYWNjZXNzX2tleV9pZCI6IjZmZDc4NDA4YjBkOTQ4ZTM5OTg5N2E3NTc2NjJkYjcxIn0.e4bM0PWiDoPNJ2ksm4KVNqr0_o4iidH8KpbOaT0p-MjoZHf9h_S4cyi3S3Ovz_WIL3XfBNY01CuWTFRe11H35zyVt630yMRoZsyIY-r6heiqiKDzPuFRE80VM9Sq2XLkKBTZYp2g8urTGfZRZt3iqhRWIVAxBZ37deTP63ZL1ep8P6XUiz1be6Xndd1peCUHDScOPGY5gixTKrBoO3AHwMZOz-FU1_T_ah4AJg9CRzli8A5VTqJuTXlTmvCNDSKk8dh10SXyRQVPWVOVhg72_TNuc5VyRPJO-GQF11n8fO5XgxhMz5ahIl0aLhX5IKkVgsD6RxKs3Wf9QGGetedcDQ&X-Amz-Signature=bdd049d22f7d99ba55d2652aec5ab4982f0961cf487c7b89f7a84398234a7de9',
       'proj:bbox': [654650.0, 5669980.0, 668240.0, 5679810.0],
       'proj:epsg': 32631,
       'proj:shape': [983, 1359],
       'raster:bands': [{'name': 'FAPAR',
         'statistics': {'maximum': 0.97713512182236,
          'mean': 0.47402824729596,
          'minimum': 0.00015301299572457,
          'stddev': 0.24429189883299,
          'valid_percent': 98.08}}],
       'roles': ['data'],
       'title': 'openEO_2020-05-15Z.tif',
       'type': 'image/tiff; application=geotiff'},
      'openEO_2020-05-17Z.tif': {'bands': [{'name': 'FAPAR'}],
       'eo:bands': [{'name': 'FAPAR'}],
       'href': 'https://s3.waw3-1.openeo.v1.dataspace.copernicus.eu/openeo-data-prod-waw4-1/batch_jobs/j-2601061058334edd8f0e6c8e4aaf1012/openEO_2020-05-17Z.tif?X-Proxy-Head-As-Get=true&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=951ee7d9969f41129ad136d024a846e1%2F20260106%2Fwaw4-1%2Fs3%2Faws4_request&X-Amz-Date=20260106T120104Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Security-Token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2FybiI6ImFybjpvcGVuZW93czppYW06Ojpyb2xlL29wZW5lby1kYXRhLXByb2Qtd2F3NC0xLXdvcmtzcGFjZSIsImluaXRpYWxfaXNzdWVyIjoib3BlbmVvLnByb2Qud2F3My0xLm9wZW5lby1pbnQudjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJodHRwczovL2F3cy5hbWF6b24uY29tL3RhZ3MiOnsicHJpbmNpcGFsX3RhZ3MiOnsiam9iX2lkIjpbImotMjYwMTA2MTA1ODMzNGVkZDhmMGU2YzhlNGFhZjEwMTIiXSwidXNlcl9pZCI6WyIzZTI0ZTI1MS0yZTlhLTQzOGYtOTBhOS1kNDUwMGU1NzY1NzQiXX0sInRyYW5zaXRpdmVfdGFnX2tleXMiOlsidXNlcl9pZCIsImpvYl9pZCJdfSwiaXNzIjoic3RzLndhdzMtMS5vcGVuZW8udjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJzdWIiOiJvcGVuZW8tZHJpdmVyIiwiZXhwIjoxNzY3NzQ0MDY0LCJuYmYiOjE3Njc3MDA4NjQsImlhdCI6MTc2NzcwMDg2NCwianRpIjoiNmFiOWI3NmQtYzIwOS00MzRhLWE3NjEtY2EyYWNmOGQ0NzY0IiwiYWNjZXNzX2tleV9pZCI6Ijk1MWVlN2Q5OTY5ZjQxMTI5YWQxMzZkMDI0YTg0NmUxIn0.L2oGO5d2l2uF76VU7xIrhxHEhqj60EAvMUEbCeqkysspRK4CfzgCjixLIe-63s4sTnhqKG1qDsBJj1h6LbWSCutlmJPQQhf4GHGIEkX50B5JGAmGQ4dSfVtvDiK2cjDXMsiECvPLFNX6pIlgRavxXizivQ9BHFJs4uEnd7fIC8FLIG_DB5XYgYvMQ9xIzGfqAXVPbSm0OmJInXMT4HIScssHqBReK_ezWK7mVEsB-J-NVTuyYVp8cvkyd_cJ9t1ZDAxVSTVIrOXUTPlquC1bwMOe2D7ak9BMJPnwfkGBmmYISaBhTRcHSPcfZrx-sO_ZbPav58UJ0VEoTKhXrzhrvQ&X-Amz-Signature=db81fda8dd86a6e645b9c7c1a9eb1d769652964eaa5b13235caea72cf4afb131',
       'proj:bbox': [654650.0, 5669980.0, 668240.0, 5679810.0],
       'proj:epsg': 32631,
       'proj:shape': [983, 1359],
       'raster:bands': [{'name': 'FAPAR',
         'statistics': {'maximum': 0.970831990242,
          'mean': 0.52552407291797,
          'minimum': 0.05854144692421,
          'stddev': 0.16173996586044,
          'valid_percent': 0.7813}}],
       'roles': ['data'],
       'title': 'openEO_2020-05-17Z.tif',
       'type': 'image/tiff; application=geotiff'},
      'openEO_2020-05-20Z.tif': {'bands': [{'name': 'FAPAR'}],
       'eo:bands': [{'name': 'FAPAR'}],
       'href': 'https://s3.waw3-1.openeo.v1.dataspace.copernicus.eu/openeo-data-prod-waw4-1/batch_jobs/j-2601061058334edd8f0e6c8e4aaf1012/openEO_2020-05-20Z.tif?X-Proxy-Head-As-Get=true&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=1a62565affb54f3787748a9863674cae%2F20260106%2Fwaw4-1%2Fs3%2Faws4_request&X-Amz-Date=20260106T120104Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Security-Token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2FybiI6ImFybjpvcGVuZW93czppYW06Ojpyb2xlL29wZW5lby1kYXRhLXByb2Qtd2F3NC0xLXdvcmtzcGFjZSIsImluaXRpYWxfaXNzdWVyIjoib3BlbmVvLnByb2Qud2F3My0xLm9wZW5lby1pbnQudjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJodHRwczovL2F3cy5hbWF6b24uY29tL3RhZ3MiOnsicHJpbmNpcGFsX3RhZ3MiOnsiam9iX2lkIjpbImotMjYwMTA2MTA1ODMzNGVkZDhmMGU2YzhlNGFhZjEwMTIiXSwidXNlcl9pZCI6WyIzZTI0ZTI1MS0yZTlhLTQzOGYtOTBhOS1kNDUwMGU1NzY1NzQiXX0sInRyYW5zaXRpdmVfdGFnX2tleXMiOlsidXNlcl9pZCIsImpvYl9pZCJdfSwiaXNzIjoic3RzLndhdzMtMS5vcGVuZW8udjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJzdWIiOiJvcGVuZW8tZHJpdmVyIiwiZXhwIjoxNzY3NzQ0MDY0LCJuYmYiOjE3Njc3MDA4NjQsImlhdCI6MTc2NzcwMDg2NCwianRpIjoiYWVhZDM5ZGEtNmVkOC00YWQ1LTk3OTktM2M5MzYyYzkyY2RlIiwiYWNjZXNzX2tleV9pZCI6IjFhNjI1NjVhZmZiNTRmMzc4Nzc0OGE5ODYzNjc0Y2FlIn0.UfPVhDuOsqKPVaWkkj235j-_5xHgpdv0FmZkNGz-YG3fNlTFtSaz9rGxAsA_pGaWKyYWyPp12v27M_AgWE3dSekr6P6bUTxtNUbKMCr7SllXSoL75Tx1Nh-yStSnebDHZdXa_8eILytq1vR-J6UMz3FxdxguDIlL3m0jzM43g7xj3jXvMaxWtveexNcrwAJT9U7F_Nh0cTjls4-WYZU0omjKpCTvXltHHOkWiJYGOAVxTicFrmMd-QymKT6ctxz3DuBcLlLwyXbQqRKTZdrMBe9GMUVKPLezlyl7yxOh0cMhWWkqPMDGBrURmzwWGSxOiwsv1tNa9caoHwgvCGU1AA&X-Amz-Signature=ba0549870738ab9ef24ead25bea51798684d1c9e42d6fd9c02195a46f0b4ff87',
       'proj:bbox': [654650.0, 5669980.0, 668240.0, 5679810.0],
       'proj:epsg': 32631,
       'proj:shape': [983, 1359],
       'raster:bands': [{'name': 'FAPAR',
         'statistics': {'maximum': 0.96466785669327,
          'mean': 0.51131852920048,
          'minimum': 0.00015301299572457,
          'stddev': 0.24046400767981,
          'valid_percent': 2.666}}],
       'roles': ['data'],
       'title': 'openEO_2020-05-20Z.tif',
       'type': 'image/tiff; application=geotiff'},
      'openEO_2020-05-25Z.tif': {'bands': [{'name': 'FAPAR'}],
       'eo:bands': [{'name': 'FAPAR'}],
       'href': 'https://s3.waw3-1.openeo.v1.dataspace.copernicus.eu/openeo-data-prod-waw4-1/batch_jobs/j-2601061058334edd8f0e6c8e4aaf1012/openEO_2020-05-25Z.tif?X-Proxy-Head-As-Get=true&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ec45444fecfd4d13bfa5189cd064e18e%2F20260106%2Fwaw4-1%2Fs3%2Faws4_request&X-Amz-Date=20260106T120104Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Security-Token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2FybiI6ImFybjpvcGVuZW93czppYW06Ojpyb2xlL29wZW5lby1kYXRhLXByb2Qtd2F3NC0xLXdvcmtzcGFjZSIsImluaXRpYWxfaXNzdWVyIjoib3BlbmVvLnByb2Qud2F3My0xLm9wZW5lby1pbnQudjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJodHRwczovL2F3cy5hbWF6b24uY29tL3RhZ3MiOnsicHJpbmNpcGFsX3RhZ3MiOnsiam9iX2lkIjpbImotMjYwMTA2MTA1ODMzNGVkZDhmMGU2YzhlNGFhZjEwMTIiXSwidXNlcl9pZCI6WyIzZTI0ZTI1MS0yZTlhLTQzOGYtOTBhOS1kNDUwMGU1NzY1NzQiXX0sInRyYW5zaXRpdmVfdGFnX2tleXMiOlsidXNlcl9pZCIsImpvYl9pZCJdfSwiaXNzIjoic3RzLndhdzMtMS5vcGVuZW8udjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJzdWIiOiJvcGVuZW8tZHJpdmVyIiwiZXhwIjoxNzY3NzQ0MDY0LCJuYmYiOjE3Njc3MDA4NjQsImlhdCI6MTc2NzcwMDg2NCwianRpIjoiZmYyYjkyODQtMTg5Yi00NGQyLWIyMjItNGI3M2Q4NDUwMjI5IiwiYWNjZXNzX2tleV9pZCI6ImVjNDU0NDRmZWNmZDRkMTNiZmE1MTg5Y2QwNjRlMThlIn0.JFk4k1RXMLp7i0H1BkTA_8aWlNrBzGdPco4R-TZmcn3uyki8FD70gAtcAv4OzNe8BXapI89zpT1Kinv-rUeRTb6s3rXDanxwNthyhBdjBen17Lm_090_ut9YjoV1bWRX8EL9KlOOcFaGEhsrfMVIgRCMH8Guzh5bIu39rU0M5xW7HjAeaUktjLHj70HH84eKwcSfJLsDDcpH8ABm9739GwByukdQ0Sv_qbt2Rg3IkRB1-ku7iwLN0KlRFK8RnC8jvM7-0T50g26OEU82EzXQUh_aG--yGPw20lyd5HugOEaYKUUeeDK2Ij1Vh5eJTmecwr8HOrS7DD0UgrjN0xNPqQ&X-Amz-Signature=094bfb9446b183b75907915773ce0f56be5fb8174b7d166157d667f9fe903ebe',
       'proj:bbox': [654650.0, 5669980.0, 668240.0, 5679810.0],
       'proj:epsg': 32631,
       'proj:shape': [983, 1359],
       'raster:bands': [{'name': 'FAPAR',
         'statistics': {'maximum': 0.9697203040123,
          'mean': 0.42006842178853,
          'minimum': 0.00015301299572457,
          'stddev': 0.29061228738001,
          'valid_percent': 2.813}}],
       'roles': ['data'],
       'title': 'openEO_2020-05-25Z.tif',
       'type': 'image/tiff; application=geotiff'},
      'openEO_2020-05-27Z.tif': {'bands': [{'name': 'FAPAR'}],
       'eo:bands': [{'name': 'FAPAR'}],
       'href': 'https://s3.waw3-1.openeo.v1.dataspace.copernicus.eu/openeo-data-prod-waw4-1/batch_jobs/j-2601061058334edd8f0e6c8e4aaf1012/openEO_2020-05-27Z.tif?X-Proxy-Head-As-Get=true&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=8c93162e8e4d4e44bf173cb6eca82502%2F20260106%2Fwaw4-1%2Fs3%2Faws4_request&X-Amz-Date=20260106T120103Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Security-Token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2FybiI6ImFybjpvcGVuZW93czppYW06Ojpyb2xlL29wZW5lby1kYXRhLXByb2Qtd2F3NC0xLXdvcmtzcGFjZSIsImluaXRpYWxfaXNzdWVyIjoib3BlbmVvLnByb2Qud2F3My0xLm9wZW5lby1pbnQudjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJodHRwczovL2F3cy5hbWF6b24uY29tL3RhZ3MiOnsicHJpbmNpcGFsX3RhZ3MiOnsiam9iX2lkIjpbImotMjYwMTA2MTA1ODMzNGVkZDhmMGU2YzhlNGFhZjEwMTIiXSwidXNlcl9pZCI6WyIzZTI0ZTI1MS0yZTlhLTQzOGYtOTBhOS1kNDUwMGU1NzY1NzQiXX0sInRyYW5zaXRpdmVfdGFnX2tleXMiOlsidXNlcl9pZCIsImpvYl9pZCJdfSwiaXNzIjoic3RzLndhdzMtMS5vcGVuZW8udjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJzdWIiOiJvcGVuZW8tZHJpdmVyIiwiZXhwIjoxNzY3NzQ0MDYzLCJuYmYiOjE3Njc3MDA4NjMsImlhdCI6MTc2NzcwMDg2MywianRpIjoiMTE0ODMzMWUtYjU1My00NGEyLTgwNzEtNjlhYTBlZTY0ZmRmIiwiYWNjZXNzX2tleV9pZCI6IjhjOTMxNjJlOGU0ZDRlNDRiZjE3M2NiNmVjYTgyNTAyIn0.OPsm5nElaLJ7YtXZDlXCSOQG-e6kC03G-tos7OYN7THK39C62GL-2iJ-gn2kNn816f3ihwsbgctN_W3Lg0XABwIAd4WvoJUvZIWRk_2A4_hdnHd5B8x01ojuJvJyNvjyDvZ73hDdQT76tWwfvyOrfi563_xB5sl-4WLTHqS8OswuycSByGMF8_OHTwKGtKoJNya6dks9IL8x6tEdYb1mqRF0VXRGQArA1O8XHwcDHsH8s-kFEHztmFW0mTiUa9wieC3LVUE-3sRSMzBuh12tJ_IuyFdzkKfchPMSuZVfvCynhk4sdo1Bh7tWlJC1PXBUN8j5wTHgrzsHEPZFDUnzMw&X-Amz-Signature=acf122d72a35cdc71964676fe094fe512ec415e004378158d3ebfffea818468f',
       'proj:bbox': [654650.0, 5669980.0, 668240.0, 5679810.0],
       'proj:epsg': 32631,
       'proj:shape': [983, 1359],
       'raster:bands': [{'name': 'FAPAR',
         'statistics': {'maximum': 0.91926145553589,
          'mean': 0.38559864139693,
          'minimum': 0.014113402925432,
          'stddev': 0.17054368732926,
          'valid_percent': 1.5}}],
       'roles': ['data'],
       'title': 'openEO_2020-05-27Z.tif',
       'type': 'image/tiff; application=geotiff'}},
     'description': 'Results for batch job j-2601061058334edd8f0e6c8e4aaf1012',
     'extent': {'spatial': {'bbox': [[5.215759, 51.160296, 5.40596, 51.244815]]},
      'temporal': {'interval': [['2020-05-06T00:00:00Z',
         '2020-05-30T00:00:00Z']]}},
     'id': 'j-2601061058334edd8f0e6c8e4aaf1012',
     'license': 'proprietary',
     'links': [{'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/10/S2A_MSIL2A_20200510T105031_N0500_R051_T31UFS_20230402T155457.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/10/S2A_MSIL2A_20200510T105031_N0500_R051_T31UFS_20230402T155457.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/17/S2A_MSIL2A_20200517T104031_N0500_R008_T31UFS_20230415T221729.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/17/S2A_MSIL2A_20200517T104031_N0500_R008_T31UFS_20230415T221729.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/12/S2B_MSIL2A_20200512T103619_N0500_R008_T31UFS_20230508T131723.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/12/S2B_MSIL2A_20200512T103619_N0500_R008_T31UFS_20230508T131723.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/27/S2A_MSIL2A_20200527T104031_N0500_R008_T31UFS_20230502T044016.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/27/S2A_MSIL2A_20200527T104031_N0500_R008_T31UFS_20230502T044016.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/20/S2A_MSIL2A_20200520T105031_N0500_R051_T31UFS_20230619T075148.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/20/S2A_MSIL2A_20200520T105031_N0500_R051_T31UFS_20230619T075148.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/22/S2B_MSIL2A_20200522T103629_N0500_R008_T31UFS_20230502T121839.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/22/S2B_MSIL2A_20200522T103629_N0500_R008_T31UFS_20230502T121839.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/15/S2B_MSIL2A_20200515T104619_N0500_R051_T31UFS_20230404T125244.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/15/S2B_MSIL2A_20200515T104619_N0500_R051_T31UFS_20230404T125244.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/07/S2A_MSIL2A_20200507T104031_N0500_R008_T31UFS_20230607T120850.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/07/S2A_MSIL2A_20200507T104031_N0500_R008_T31UFS_20230607T120850.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/25/S2B_MSIL2A_20200525T104619_N0500_R051_T31UFS_20230508T132440.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/25/S2B_MSIL2A_20200525T104619_N0500_R051_T31UFS_20230508T132440.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/10/S2A_MSIL2A_20200510T105031_N0500_R051_T31UFS_20230402T155457.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/10/S2A_MSIL2A_20200510T105031_N0500_R051_T31UFS_20230402T155457.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/17/S2A_MSIL2A_20200517T104031_N0500_R008_T31UFS_20230415T221729.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/17/S2A_MSIL2A_20200517T104031_N0500_R008_T31UFS_20230415T221729.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/12/S2B_MSIL2A_20200512T103619_N0500_R008_T31UFS_20230508T131723.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/12/S2B_MSIL2A_20200512T103619_N0500_R008_T31UFS_20230508T131723.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/27/S2A_MSIL2A_20200527T104031_N0500_R008_T31UFS_20230502T044016.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/27/S2A_MSIL2A_20200527T104031_N0500_R008_T31UFS_20230502T044016.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/20/S2A_MSIL2A_20200520T105031_N0500_R051_T31UFS_20230619T075148.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/20/S2A_MSIL2A_20200520T105031_N0500_R051_T31UFS_20230619T075148.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/22/S2B_MSIL2A_20200522T103629_N0500_R008_T31UFS_20230502T121839.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/22/S2B_MSIL2A_20200522T103629_N0500_R008_T31UFS_20230502T121839.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/15/S2B_MSIL2A_20200515T104619_N0500_R051_T31UFS_20230404T125244.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/15/S2B_MSIL2A_20200515T104619_N0500_R051_T31UFS_20230404T125244.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/07/S2A_MSIL2A_20200507T104031_N0500_R008_T31UFS_20230607T120850.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/07/S2A_MSIL2A_20200507T104031_N0500_R008_T31UFS_20230607T120850.SAFE',
       'type': 'application/json'},
      {'href': '/eodata/Sentinel-2/MSI/L2A_N0500/2020/05/25/S2B_MSIL2A_20200525T104619_N0500_R051_T31UFS_20230508T132440.SAFE',
       'rel': 'derived_from',
       'title': 'Derived from /eodata/Sentinel-2/MSI/L2A_N0500/2020/05/25/S2B_MSIL2A_20200525T104619_N0500_R051_T31UFS_20230508T132440.SAFE',
       'type': 'application/json'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results',
       'rel': 'self',
       'type': 'application/json'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results/M2UyNGUyNTEtMmU5YS00MzhmLTkwYTktZDQ1MDBlNTc2NTc0/d2dbfae1022a60f149fa57bedba3e092?expires=1768305662',
       'rel': 'canonical',
       'type': 'application/json'},
      {'href': 'http://ceos.org/ard/files/PFS/SR/v5.0/CARD4L_Product_Family_Specification_Surface_Reflectance-v5.0.pdf',
       'rel': 'card4l-document',
       'type': 'application/pdf'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results/items/M2UyNGUyNTEtMmU5YS00MzhmLTkwYTktZDQ1MDBlNTc2NTc0/3ed1c8d5bbd3cf0d0dc1cb28f3cc082c/openEO_2020-05-15Z.tif?expires=1768305664',
       'rel': 'item',
       'type': 'application/geo+json'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results/items/M2UyNGUyNTEtMmU5YS00MzhmLTkwYTktZDQ1MDBlNTc2NTc0/b771135d6e952edcda07b7f37a694234/openEO_2020-05-27Z.tif?expires=1768305664',
       'rel': 'item',
       'type': 'application/geo+json'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results/items/M2UyNGUyNTEtMmU5YS00MzhmLTkwYTktZDQ1MDBlNTc2NTc0/a9bd45c0de2bcceecacb22adebb129e4/openEO_2020-05-25Z.tif?expires=1768305664',
       'rel': 'item',
       'type': 'application/geo+json'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results/items/M2UyNGUyNTEtMmU5YS00MzhmLTkwYTktZDQ1MDBlNTc2NTc0/9410c952ec1aedb656ae8bbf2e2b13af/openEO_2020-05-17Z.tif?expires=1768305664',
       'rel': 'item',
       'type': 'application/geo+json'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results/items/M2UyNGUyNTEtMmU5YS00MzhmLTkwYTktZDQ1MDBlNTc2NTc0/ea9b983fd9571cb6416cbb2c0ccefaa4/openEO_2020-05-07Z.tif?expires=1768305664',
       'rel': 'item',
       'type': 'application/geo+json'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results/items/M2UyNGUyNTEtMmU5YS00MzhmLTkwYTktZDQ1MDBlNTc2NTc0/b93ae13c7295bdea8100576882bafc95/openEO_2020-05-20Z.tif?expires=1768305664',
       'rel': 'item',
       'type': 'application/geo+json'},
      {'href': 'https://openeo.dataspace.copernicus.eu/openeo/1.2/jobs/j-2601061058334edd8f0e6c8e4aaf1012/results/items/M2UyNGUyNTEtMmU5YS00MzhmLTkwYTktZDQ1MDBlNTc2NTc0/8341ed40ff3738d89da579167c891dc9/openEO_2020-05-12Z.tif?expires=1768305664',
       'rel': 'item',
       'type': 'application/geo+json'}],
     'openeo:status': 'finished',
     'providers': [{'description': 'This data was processed on an openEO backend maintained by VITO.',
       'name': 'VITO',
       'processing:expression': {'expression': {'biopar1': {'arguments': {'biopar_type': 'FAPAR',
           'spatial_extent': {'east': 5.40596,
            'north': 51.244815,
            'south': 51.160296,
            'west': 5.215759},
           'temporal_extent': ['2020-05-06', '2020-05-30']},
          'namespace': 'https://raw.githubusercontent.com/ESA-APEx/apex_algorithms/refs/heads/main/algorithm_catalog/vito/biopar/openeo_udp/biopar.json',
          'process_id': 'biopar'},
         'saveresult1': {'arguments': {'data': {'from_node': 'biopar1'},
           'format': 'GTiff',
           'options': {}},
          'process_id': 'save_result',
          'result': True}},
        'format': 'openeo'},
       'processing:facility': 'openEO Geotrellis backend',
       'processing:software': {'Geotrellis backend': '0.70.0a7'},
       'roles': ['processor']}],
     'stac_extensions': ['https://stac-extensions.github.io/eo/v1.1.0/schema.json',
      'https://stac-extensions.github.io/file/v2.1.0/schema.json',
      'https://stac-extensions.github.io/processing/v1.1.0/schema.json',
      'https://stac-extensions.github.io/projection/v1.1.0/schema.json'],
     'stac_version': '1.0.0',
     'summaries': {},
     'title': 'BIOPAR_FAPAR_Job',
     'type': 'Collection'}

Either you can download the result by clicking the download link from the result metadata or use `download_files()` method to download the result programmatically.

``` python
results.download_files("data/fapar")
```

    [WindowsPath('data/fapar/openEO_2020-05-07Z.tif'),
     WindowsPath('data/fapar/openEO_2020-05-12Z.tif'),
     WindowsPath('data/fapar/openEO_2020-05-15Z.tif'),
     WindowsPath('data/fapar/openEO_2020-05-17Z.tif'),
     WindowsPath('data/fapar/openEO_2020-05-20Z.tif'),
     WindowsPath('data/fapar/openEO_2020-05-25Z.tif'),
     WindowsPath('data/fapar/openEO_2020-05-27Z.tif'),
     WindowsPath('data/fapar/job-results.json')]

## Quick visualization

``` python
import rasterio
import rasterio.plot
import matplotlib.pyplot as plt

tif_file = "data/fapar/openEO_2020-05-07Z.tif"

with rasterio.open(tif_file) as src:
    data = src.read(1)
    extent = rasterio.plot.plotting_extent(src)

plt.imshow(data, cmap="YlGn", extent=extent)
plt.title("FAPAR")
plt.show()
```

![](biopar_service_files/figure-html/cell-9-output-1.png)
