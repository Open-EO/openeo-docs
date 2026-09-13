# Execute openEO Jobs

Submit, monitor, and retrieve a process graph

A process graph becomes useful when it is executed. Use synchronous requests for very small explorations and batch jobs for real analyses.

VITO

EODC

CDSE

Sentinel Hub

> **NOTE:**
>
> The buttons on this page are a documentation aid, not a live capability registry. Use the [openEO Hub](https://hub.openeo.org/) for a cross-backend overview: open **Filters**, select a process under **Processes**, and the Hub shows only matching services. The Hub data is crawled and cached.

## Run a batch job

Use a batch job for large spatial extents, long time series, UDFs, and preprocessing that may exceed synchronous request limits. The backend records logs and result assets while the job runs, so the workflow can be monitored and retried independently of the client connection.

### Python

``` python
job = result.create_job(
    out_format="GTiff",
    title="Monthly NDVI composite",
    description="A monthly median NDVI workflow",
)
job.start_and_wait()
job.get_results().download_files("./output")
```

> **TIP:**
>
> Filter space, time, and bands before computationally intensive processes. Test a small area first, then submit the final workflow as a batch job. Inspect job logs when a backend reports an error.

`save_result` defines the output format inside a process graph; job creation controls when and how the backend executes it. Review the backend’s supported output formats and job limits before a large run.
