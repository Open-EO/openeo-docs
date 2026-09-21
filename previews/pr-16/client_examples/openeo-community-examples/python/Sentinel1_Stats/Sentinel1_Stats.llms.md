# Publishing an openEO workflow as a User-Defined-Process (UDP)

In this notebook, we want to show how to create an openEO User Defined Process(UDP). Here, we make use of an apply_dimension process that applies a process to all values along a dimension of a data cube.

The notebook involves a section on creating a concrete datacube, inspecting netCDF downloads, and developing a parameterized version stored as a UDP.

``` python
import json
import openeo
import xarray
import matplotlib.pyplot as plt
from utils import *

from openeo.processes import array_create, array_concat, ProcessBuilder
from openeo.api.process import Parameter
```

If you have a local JupyterLab instance running, you need to install the following libraries first: openeo, xarray, ipyleaflet, shapely and matplotlib:

`pip install openeo xarray shapely ipyleaflet matplotlib`

Make sure to restart the kernel and refresh the webpage.

``` python
# Set some defaults for plots
plt.rcParams["figure.figsize"] = [5.0, 3.0]
plt.rcParams["figure.dpi"] = 75
```

Connect to the openEO Platform backend (at [openeo.cloud](https://openeo.cloud/)) and authenticate with OIDC.

``` python
connection = openeo.connect("openeofed.dataspace.copernicus.eu").authenticate_oidc()
```

    Authenticated using refresh token.

## Inspect raw data

Load initial data cube with raw `S1_GRD_SIGMA0_ASCENDING` data for a certain spatio-temporal extent.

``` python
center = [46.49, 11.35]
zoom = 15

eoMap = openeoMap(center, zoom)
eoMap.map
```

``` python
bbox = eoMap.getBbox()
print("west", bbox[0], "\neast", bbox[2], "\nsouth", bbox[1], "\nnorth", bbox[3])
```

``` python
spatial_extent = {
    "west": 11.3409 ,
    "east": 11.353779 ,
    "south": 46.48772 ,
    "north": 46.493924,
    "crs": 4326,
}
temporal_extent = ["2023-05-01", "2023-07-01"]
```

``` python
spatial_extent = {
    "west": bbox[0],
    "east": bbox[2],
    "south": bbox[1],
    "north": bbox[3],
    "crs": 4326,
}
temporal_extent = ["2023-05-01", "2023-07-01"]
```

``` python
s1_raw = connection.load_collection(
    collection_id="SENTINEL1_GRD",
    temporal_extent=temporal_extent,
    spatial_extent=spatial_extent,
    bands=["VH", "VV"],
)
```

Let’s download this data cube synchronously as a netCDF file.

This download command triggers the actual processing on the back-end: it sends the process graph to the back-end and waits for the result. It is a synchronous operation (the download() call blocks until the result is fully downloaded) and because we work on a small spatio-temporal extent, this should only take a couple of seconds.

``` python
%%time
s1_raw.download("s1sar-raw.nc")
```

    CPU times: user 12.6 ms, sys: 9.67 ms, total: 22.3 ms
    Wall time: 46.5 s

However, [batch job-based execution](https://open-eo.github.io/openeo-python-client/batch_jobs.html) is preferred when it is relatively larger spatial/temporal extent and the process may take some time to process.

``` python
ds = xarray.load_dataset("s1sar-raw.nc")
ds
```

    sh: line 1: getfattr: command not found

![](data:image/svg+xml;base64,PHN2ZyBzdHlsZT0icG9zaXRpb246IGFic29sdXRlOyB3aWR0aDogMDsgaGVpZ2h0OiAwOyBvdmVyZmxvdzogaGlkZGVuIj4KPGRlZnM+CjxzeW1ib2wgaWQ9Imljb24tZGF0YWJhc2UiIHZpZXdib3g9IjAgMCAzMiAzMiI+CjxwYXRoIGQ9Ik0xNiAwYy04LjgzNyAwLTE2IDIuMjM5LTE2IDV2NGMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di00YzAtMi43NjEtNy4xNjMtNS0xNi01eiIgLz4KPHBhdGggZD0iTTE2IDE3Yy04LjgzNyAwLTE2LTIuMjM5LTE2LTV2NmMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di02YzAgMi43NjEtNy4xNjMgNS0xNiA1eiIgLz4KPHBhdGggZD0iTTE2IDI2Yy04LjgzNyAwLTE2LTIuMjM5LTE2LTV2NmMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di02YzAgMi43NjEtNy4xNjMgNS0xNiA1eiIgLz4KPC9zeW1ib2w+CjxzeW1ib2wgaWQ9Imljb24tZmlsZS10ZXh0MiIgdmlld2JveD0iMCAwIDMyIDMyIj4KPHBhdGggZD0iTTI4LjY4MSA3LjE1OWMtMC42OTQtMC45NDctMS42NjItMi4wNTMtMi43MjQtMy4xMTZzLTIuMTY5LTIuMDMwLTMuMTE2LTIuNzI0Yy0xLjYxMi0xLjE4Mi0yLjM5My0xLjMxOS0yLjg0MS0xLjMxOWgtMTUuNWMtMS4zNzggMC0yLjUgMS4xMjEtMi41IDIuNXYyN2MwIDEuMzc4IDEuMTIyIDIuNSAyLjUgMi41aDIzYzEuMzc4IDAgMi41LTEuMTIyIDIuNS0yLjV2LTE5LjVjMC0wLjQ0OC0wLjEzNy0xLjIzLTEuMzE5LTIuODQxek0yNC41NDMgNS40NTdjMC45NTkgMC45NTkgMS43MTIgMS44MjUgMi4yNjggMi41NDNoLTQuODExdi00LjgxMWMwLjcxOCAwLjU1NiAxLjU4NCAxLjMwOSAyLjU0MyAyLjI2OHpNMjggMjkuNWMwIDAuMjcxLTAuMjI5IDAuNS0wLjUgMC41aC0yM2MtMC4yNzEgMC0wLjUtMC4yMjktMC41LTAuNXYtMjdjMC0wLjI3MSAwLjIyOS0wLjUgMC41LTAuNSAwIDAgMTUuNDk5LTAgMTUuNSAwdjdjMCAwLjU1MiAwLjQ0OCAxIDEgMWg3djE5LjV6IiAvPgo8cGF0aCBkPSJNMjMgMjZoLTE0Yy0wLjU1MiAwLTEtMC40NDgtMS0xczAuNDQ4LTEgMS0xaDE0YzAuNTUyIDAgMSAwLjQ0OCAxIDFzLTAuNDQ4IDEtMSAxeiIgLz4KPHBhdGggZD0iTTIzIDIyaC0xNGMtMC41NTIgMC0xLTAuNDQ4LTEtMXMwLjQ0OC0xIDEtMWgxNGMwLjU1MiAwIDEgMC40NDggMSAxcy0wLjQ0OCAxLTEgMXoiIC8+CjxwYXRoIGQ9Ik0yMyAxOGgtMTRjLTAuNTUyIDAtMS0wLjQ0OC0xLTFzMC40NDgtMSAxLTFoMTRjMC41NTIgMCAxIDAuNDQ4IDEgMXMtMC40NDggMS0xIDF6IiAvPgo8L3N5bWJvbD4KPC9kZWZzPgo8L3N2Zz4=)

``` xr-text-repr-fallback
<xarray.Dataset> Size: 2MB
Dimensions:  (t: 15, x: 102, y: 72)
Coordinates:
  * t        (t) datetime64[ns] 120B 2023-05-03 2023-05-10 ... 2023-06-28
  * x        (x) float64 816B 6.796e+05 6.796e+05 ... 6.806e+05 6.806e+05
  * y        (y) float64 576B 5.152e+06 5.152e+06 ... 5.151e+06 5.151e+06
Data variables:
    crs      |S1 1B b''
    VH       (t, y, x) float64 881kB 0.3058 0.2208 0.285 ... 0.06232 0.06846
    VV       (t, y, x) float64 881kB 0.2863 0.4197 1.002 ... 1.068 1.072 1.145
Attributes:
    Conventions:  CF-1.9
    institution:  openEO platform
```

xarray.Dataset

Dimensions:

- t: 15
- x: 102
- y: 72

Coordinates: (3)

t

\(t\)

datetime64\[ns\]

2023-05-03 ... 2023-06-28

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
t

long_name :  
t

axis :  
T

    array(['2023-05-03T00:00:00.000000000', '2023-05-10T00:00:00.000000000',
           '2023-05-11T00:00:00.000000000', '2023-05-15T00:00:00.000000000',
           '2023-05-22T00:00:00.000000000', '2023-05-23T00:00:00.000000000',
           '2023-05-27T00:00:00.000000000', '2023-06-03T00:00:00.000000000',
           '2023-06-04T00:00:00.000000000', '2023-06-08T00:00:00.000000000',
           '2023-06-15T00:00:00.000000000', '2023-06-16T00:00:00.000000000',
           '2023-06-20T00:00:00.000000000', '2023-06-27T00:00:00.000000000',
           '2023-06-28T00:00:00.000000000'], dtype='datetime64[ns]')

x

\(x\)

float64

6.796e+05 6.796e+05 ... 6.806e+05

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
projection_x_coordinate

long_name :  
x coordinate of projection

units :  
m

    array([679635., 679645., 679655., 679665., 679675., 679685., 679695., 679705.,
           679715., 679725., 679735., 679745., 679755., 679765., 679775., 679785.,
           679795., 679805., 679815., 679825., 679835., 679845., 679855., 679865.,
           679875., 679885., 679895., 679905., 679915., 679925., 679935., 679945.,
           679955., 679965., 679975., 679985., 679995., 680005., 680015., 680025.,
           680035., 680045., 680055., 680065., 680075., 680085., 680095., 680105.,
           680115., 680125., 680135., 680145., 680155., 680165., 680175., 680185.,
           680195., 680205., 680215., 680225., 680235., 680245., 680255., 680265.,
           680275., 680285., 680295., 680305., 680315., 680325., 680335., 680345.,
           680355., 680365., 680375., 680385., 680395., 680405., 680415., 680425.,
           680435., 680445., 680455., 680465., 680475., 680485., 680495., 680505.,
           680515., 680525., 680535., 680545., 680555., 680565., 680575., 680585.,
           680595., 680605., 680615., 680625., 680635., 680645.])

y

\(y\)

float64

5.152e+06 5.152e+06 ... 5.151e+06

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
projection_y_coordinate

long_name :  
y coordinate of projection

units :  
m

    array([5151615., 5151605., 5151595., 5151585., 5151575., 5151565., 5151555.,
           5151545., 5151535., 5151525., 5151515., 5151505., 5151495., 5151485.,
           5151475., 5151465., 5151455., 5151445., 5151435., 5151425., 5151415.,
           5151405., 5151395., 5151385., 5151375., 5151365., 5151355., 5151345.,
           5151335., 5151325., 5151315., 5151305., 5151295., 5151285., 5151275.,
           5151265., 5151255., 5151245., 5151235., 5151225., 5151215., 5151205.,
           5151195., 5151185., 5151175., 5151165., 5151155., 5151145., 5151135.,
           5151125., 5151115., 5151105., 5151095., 5151085., 5151075., 5151065.,
           5151055., 5151045., 5151035., 5151025., 5151015., 5151005., 5150995.,
           5150985., 5150975., 5150965., 5150955., 5150945., 5150935., 5150925.,
           5150915., 5150905.])

Data variables: (3)

crs

()

\|S1

b''

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

crs_wkt :  
PROJCS\["WGS 84 / UTM zone 32N", GEOGCS\["WGS 84", DATUM\["World Geodetic System 1984", SPHEROID\["WGS 84", 6378137.0, 298.257223563, AUTHORITY\["EPSG","7030"\]\], AUTHORITY\["EPSG","6326"\]\], PRIMEM\["Greenwich", 0.0, AUTHORITY\["EPSG","8901"\]\], UNIT\["degree", 0.017453292519943295\], AXIS\["Geodetic longitude", EAST\], AXIS\["Geodetic latitude", NORTH\], AUTHORITY\["EPSG","4326"\]\], PROJECTION\["Transverse_Mercator", AUTHORITY\["EPSG","9807"\]\], PARAMETER\["central_meridian", 9.0\], PARAMETER\["latitude_of_origin", 0.0\], PARAMETER\["scale_factor", 0.9996\], PARAMETER\["false_easting", 500000.0\], PARAMETER\["false_northing", 0.0\], UNIT\["m", 1.0\], AXIS\["Easting", EAST\], AXIS\["Northing", NORTH\], AUTHORITY\["EPSG","32632"\]\]

spatial_ref :  
PROJCS\["WGS 84 / UTM zone 32N", GEOGCS\["WGS 84", DATUM\["World Geodetic System 1984", SPHEROID\["WGS 84", 6378137.0, 298.257223563, AUTHORITY\["EPSG","7030"\]\], AUTHORITY\["EPSG","6326"\]\], PRIMEM\["Greenwich", 0.0, AUTHORITY\["EPSG","8901"\]\], UNIT\["degree", 0.017453292519943295\], AXIS\["Geodetic longitude", EAST\], AXIS\["Geodetic latitude", NORTH\], AUTHORITY\["EPSG","4326"\]\], PROJECTION\["Transverse_Mercator", AUTHORITY\["EPSG","9807"\]\], PARAMETER\["central_meridian", 9.0\], PARAMETER\["latitude_of_origin", 0.0\], PARAMETER\["scale_factor", 0.9996\], PARAMETER\["false_easting", 500000.0\], PARAMETER\["false_northing", 0.0\], UNIT\["m", 1.0\], AXIS\["Easting", EAST\], AXIS\["Northing", NORTH\], AUTHORITY\["EPSG","32632"\]\]

    array(b'', dtype='|S1')

VH

(t, y, x)

float64

0.3058 0.2208 ... 0.06232 0.06846

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH

units :  

grid_mapping :  
crs

    array([[[0.30578476, 0.22083062, 0.28495011, ..., 0.00601044,
             0.01257194, 0.00817836],
            [0.20336124, 0.22264814, 0.28441703, ..., 0.00559112,
             0.02342164, 0.03505036],
            [0.20157108, 0.13497874, 0.1068417 , ..., 0.02194775,
             0.04301089, 0.07700071],
            ...,
            [0.00973709, 0.00503796, 0.00837925, ..., 0.00031839,
             0.00376074, 0.02171872],
            [0.00837886, 0.00856237, 0.01204343, ..., 0.00277543,
             0.00142006, 0.02297933],
            [0.00856518, 0.01122371, 0.01542545, ..., 0.00726967,
             0.00068292, 0.01957845]],

           [[0.07469705, 0.09299496, 0.14772725, ..., 0.03957959,
             0.02613423, 0.01661777],
            [0.05525584, 0.05894169, 0.07370081, ..., 0.07654878,
             0.04764543, 0.03578481],
            [0.10178098, 0.07179623, 0.05917186, ..., 0.07292594,
             0.04804473, 0.05707282],
    ...
            [0.03130125, 0.03628872, 0.03952755, ..., 0.00169996,
             0.00723861, 0.00780787],
            [0.02120653, 0.02419831, 0.04764988, ..., 0.00525496,
             0.00357877, 0.00879617],
            [0.01029695, 0.01121287, 0.01648132, ..., 0.00856866,
             0.00248022, 0.00702397]],

           [[0.04733023, 0.06280609, 0.06999058, ..., 0.00641829,
             0.01117368, 0.01003172],
            [0.02434754, 0.03060355, 0.04246219, ..., 0.01287112,
             0.01378713, 0.01353737],
            [0.02164285, 0.02079906, 0.02840142, ..., 0.01395037,
             0.01381883, 0.01567465],
            ...,
            [0.01505244, 0.01991274, 0.01542514, ..., 0.15768652,
             0.14829549, 0.14109968],
            [0.02350285, 0.02351517, 0.00995847, ..., 0.10264232,
             0.08775876, 0.0746175 ],
            [0.0228368 , 0.02192629, 0.01359094, ..., 0.05828236,
             0.06231741, 0.06846032]]])

VV

(t, y, x)

float64

0.2863 0.4197 1.002 ... 1.072 1.145

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV

units :  

grid_mapping :  
crs

    array([[[0.28627682, 0.41974923, 1.00157261, ..., 0.24680357,
             0.08568972, 0.04044454],
            [0.67165387, 0.57030499, 0.51492178, ..., 0.1744507 ,
             0.05387724, 0.0682224 ],
            [0.76104087, 0.60692006, 0.56552398, ..., 0.12725115,
             0.05432061, 0.08109142],
            ...,
            [0.08845934, 0.09865014, 0.08305532, ..., 0.01240802,
             0.00882796, 0.0460228 ],
            [0.05161391, 0.05707713, 0.04829733, ..., 0.02078906,
             0.01053583, 0.04757012],
            [0.0522717 , 0.06540528, 0.06209464, ..., 0.02206398,
             0.01228463, 0.02849091]],

           [[0.59334594, 0.63139158, 1.20176804, ..., 0.21536502,
             0.10467153, 0.04661704],
            [0.36914822, 0.38960469, 0.56326002, ..., 0.23207396,
             0.13010627, 0.07558577],
            [0.3913084 , 0.50614417, 0.81718516, ..., 0.14858565,
             0.11662126, 0.10953296],
    ...
            [0.07546599, 0.08640213, 0.08373421, ..., 0.02884771,
             0.01888795, 0.0666521 ],
            [0.05208195, 0.11719208, 0.15254971, ..., 0.03226842,
             0.01245109, 0.06072526],
            [0.07249771, 0.09560843, 0.06773217, ..., 0.03674552,
             0.0215037 , 0.04752812]],

           [[0.4608672 , 0.47568667, 0.46542484, ..., 0.10046628,
             0.07250372, 0.06289441],
            [0.26003391, 0.32770583, 0.40199661, ..., 0.08007107,
             0.03525665, 0.04549096],
            [0.24082465, 0.31407189, 0.37282252, ..., 0.11711237,
             0.03557625, 0.05282841],
            ...,
            [0.1110431 , 0.10369646, 0.13788435, ..., 0.50082976,
             0.52201301, 0.47967386],
            [0.07739844, 0.09985465, 0.10789572, ..., 0.69436234,
             0.81499875, 0.93010664],
            [0.12480994, 0.07786189, 0.11251473, ..., 1.06845927,
             1.07151592, 1.14460146]]])

Indexes: (3)

t

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(DatetimeIndex(['2023-05-03', '2023-05-10', '2023-05-11', '2023-05-15',
                   '2023-05-22', '2023-05-23', '2023-05-27', '2023-06-03',
                   '2023-06-04', '2023-06-08', '2023-06-15', '2023-06-16',
                   '2023-06-20', '2023-06-27', '2023-06-28'],
                  dtype='datetime64[ns]', name='t', freq=None))

x

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(Index([679635.0, 679645.0, 679655.0, 679665.0, 679675.0, 679685.0, 679695.0,
           679705.0, 679715.0, 679725.0,
           ...
           680555.0, 680565.0, 680575.0, 680585.0, 680595.0, 680605.0, 680615.0,
           680625.0, 680635.0, 680645.0],
          dtype='float64', name='x', length=102))

y

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(Index([5151615.0, 5151605.0, 5151595.0, 5151585.0, 5151575.0, 5151565.0,
           5151555.0, 5151545.0, 5151535.0, 5151525.0, 5151515.0, 5151505.0,
           5151495.0, 5151485.0, 5151475.0, 5151465.0, 5151455.0, 5151445.0,
           5151435.0, 5151425.0, 5151415.0, 5151405.0, 5151395.0, 5151385.0,
           5151375.0, 5151365.0, 5151355.0, 5151345.0, 5151335.0, 5151325.0,
           5151315.0, 5151305.0, 5151295.0, 5151285.0, 5151275.0, 5151265.0,
           5151255.0, 5151245.0, 5151235.0, 5151225.0, 5151215.0, 5151205.0,
           5151195.0, 5151185.0, 5151175.0, 5151165.0, 5151155.0, 5151145.0,
           5151135.0, 5151125.0, 5151115.0, 5151105.0, 5151095.0, 5151085.0,
           5151075.0, 5151065.0, 5151055.0, 5151045.0, 5151035.0, 5151025.0,
           5151015.0, 5151005.0, 5150995.0, 5150985.0, 5150975.0, 5150965.0,
           5150955.0, 5150945.0, 5150935.0, 5150925.0, 5150915.0, 5150905.0],
          dtype='float64', name='y'))

Attributes: (2)

Conventions :  
CF-1.9

institution :  
openEO platform

We got these observations dates:

``` python
ds.coords["t"].values
```

    array(['2023-05-03T00:00:00.000000000', '2023-05-10T00:00:00.000000000',
           '2023-05-11T00:00:00.000000000', '2023-05-15T00:00:00.000000000',
           '2023-05-22T00:00:00.000000000', '2023-05-23T00:00:00.000000000',
           '2023-05-27T00:00:00.000000000', '2023-06-03T00:00:00.000000000',
           '2023-06-04T00:00:00.000000000', '2023-06-08T00:00:00.000000000',
           '2023-06-15T00:00:00.000000000', '2023-06-16T00:00:00.000000000',
           '2023-06-20T00:00:00.000000000', '2023-06-27T00:00:00.000000000',
           '2023-06-28T00:00:00.000000000'], dtype='datetime64[ns]')

A quick plot for visual inspection.

``` python
ds["VH"].isel(t=0).plot(vmin=0, vmax=0.5)
```

![](Sentinel1_Stats_files/figure-html/cell-13-output-1.png)

This section presented a straightforward example of retrieving and analyzing a `S1_GRD_SIGMA0_ASCENDING` data cube from the backend within a defined area of interest during a specified time frame.

## Collect statistics

As part of more detailed processing within the openEO platform, we’ll gather temporal statistics using the `apply_dimension` process and a collection of statistical measures (minimum, maximum, quantiles, …).

``` python
def get_stats(data: ProcessBuilder) -> ProcessBuilder:
    """
    Collect stats for `data` (to be interpreted as an array of values along the "t" dimension).
    We should return a new array with the stats.
    """
    # Put some scalar stats (`min`, `max`, ... return a scalar value) in a new array
    scalar_stats = array_create(
        [
            data.min(),
            data.max(),
            data.mean(),
            data.sd(),
        ]
    )
    # The `quantiles` process returns an array on its own
    quantile_stats = data.quantiles([0.1, 0.5, 0.9])

    # Combine everything in a single array
    return array_concat(array1=scalar_stats, array2=quantile_stats)
```

``` python
s1_stats = s1_raw.apply_dimension(
    process=get_stats,
    dimension="t",
    target_dimension="bands",
)
# Rename band labels, pairing original band names with stat names
s1_stats = s1_stats.rename_labels(
    "bands",
    [
        f"{b}_{s}"
        for b in s1_raw.metadata.band_names
        for s in ["min", "max", "mean", "sd", "q10", "q50", "q90"]
    ],
)
```

``` python
# %%time
# s1_stats.download("s1grd-stats.nc")

# let's try batch job based execution in this process

job = s1_stats.execute_batch(
    title="Sentinel1_GRD_Statistics", outputfile="S1grd-stats.nc"
)


# # Alternatively if you want to seperately save process metadata
# s1_stats = s1_stats.save_result(format="netcdf")
# job = s1_stats.execute_batch(title="Sentinel 1 Statistics")

# # fetch your results

# results = job.get_results()
# results.download_files("output/batch_job")
```

    0:00:00 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': send 'start'
    0:00:03 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': queued (progress 0%)
    0:00:08 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': queued (progress 0%)
    0:00:15 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': queued (progress 0%)
    0:00:23 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': queued (progress 0%)
    0:00:33 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': queued (progress 0%)
    0:00:46 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': queued (progress 0%)
    0:01:01 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': queued (progress 0%)
    0:01:21 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': running (progress N/A)
    0:01:45 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': running (progress N/A)
    0:02:15 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': running (progress N/A)
    0:02:52 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': running (progress N/A)
    0:03:39 Job 'cdse-j-2607131822044818b59ca5d7a2247f8b': finished (progress 100%)

``` python
assets = job.get_results().get_assets()
print(assets[0].href)
```

    https://s3.waw3-1.openeo.v1.dataspace.copernicus.eu/openeo-data-prod-waw4-1/batch_jobs/j-2607131822044818b59ca5d7a2247f8b/openEO.nc?X-Proxy-Head-As-Get=true&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=92e5a22641de41939bd6e0089c8504c2%2F20260713%2Fwaw4-1%2Fs3%2Faws4_request&X-Amz-Date=20260713T182545Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Security-Token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlX2FybiI6ImFybjpvcGVuZW93czppYW06Ojpyb2xlL29wZW5lby1kYXRhLXByb2Qtd2F3NC0xLXdvcmtzcGFjZSIsImluaXRpYWxfaXNzdWVyIjoib3BlbmVvLnByb2Qud2F3My0xLm9wZW5lby1pbnQudjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJodHRwczovL2F3cy5hbWF6b24uY29tL3RhZ3MiOnsicHJpbmNpcGFsX3RhZ3MiOnsiam9iX2lkIjpbImotMjYwNzEzMTgyMjA0NDgxOGI1OWNhNWQ3YTIyNDdmOGIiXSwidXNlcl9pZCI6WyIzZTI0ZTI1MS0yZTlhLTQzOGYtOTBhOS1kNDUwMGU1NzY1NzQiXX0sInRyYW5zaXRpdmVfdGFnX2tleXMiOlsidXNlcl9pZCIsImpvYl9pZCJdfSwiaXNzIjoic3RzLndhdzMtMS5vcGVuZW8udjEuZGF0YXNwYWNlLmNvcGVybmljdXMuZXUiLCJzdWIiOiJvcGVuZW8tZHJpdmVyIiwiZXhwIjoxNzg0MDEwMzQ0LCJuYmYiOjE3ODM5NjcxNDQsImlhdCI6MTc4Mzk2NzE0NCwianRpIjoiNjNmMTliMTAtYzIyNC00YzBlLTk4YzktYmUzNDk3OTI1ODZhIiwiYWNjZXNzX2tleV9pZCI6IjkyZTVhMjI2NDFkZTQxOTM5YmQ2ZTAwODljODUwNGMyIn0.VT7D-agN_LsEmOWF2CYhT5X5KzVPbjvNLDps35XhhgMUKJr8DkmV1g6nNkE0Hwn5Drb0AV46UlNy5qpBrmkeEMe0-w_z5YEGZmpe7TmrobVGTergXODcF_nBIpxJS-YyzNFfLMNjQmX7KKG5ft_4tAQ3nMMzWNJVsIa25-nmpg41qHZYUDj2pO9IQFqBi3o22G29l8vAWBh92Z6FmgDO__7_3Nu43iGwG0KMYXQO8IlgvwoEhFskBExXFHr0aGLVZzB_pK3n3zukhCpn7m1ZAWfV8LUObuNutRMr_VEx89AAy_gZHWEBZ5VlfPuNin3UXFL3ycJjTJ752tsFA9_ATQ&X-Amz-Signature=11f0a73b55323cc5567ca0751f1c804fd6ec9c8600ea5eed28e8de96f28c077d

``` python
ds = xarray.load_dataset("S1grd-stats.nc").drop_vars("crs")
ds
```

    sh: line 1: getfattr: command not found

![](data:image/svg+xml;base64,PHN2ZyBzdHlsZT0icG9zaXRpb246IGFic29sdXRlOyB3aWR0aDogMDsgaGVpZ2h0OiAwOyBvdmVyZmxvdzogaGlkZGVuIj4KPGRlZnM+CjxzeW1ib2wgaWQ9Imljb24tZGF0YWJhc2UiIHZpZXdib3g9IjAgMCAzMiAzMiI+CjxwYXRoIGQ9Ik0xNiAwYy04LjgzNyAwLTE2IDIuMjM5LTE2IDV2NGMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di00YzAtMi43NjEtNy4xNjMtNS0xNi01eiIgLz4KPHBhdGggZD0iTTE2IDE3Yy04LjgzNyAwLTE2LTIuMjM5LTE2LTV2NmMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di02YzAgMi43NjEtNy4xNjMgNS0xNiA1eiIgLz4KPHBhdGggZD0iTTE2IDI2Yy04LjgzNyAwLTE2LTIuMjM5LTE2LTV2NmMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di02YzAgMi43NjEtNy4xNjMgNS0xNiA1eiIgLz4KPC9zeW1ib2w+CjxzeW1ib2wgaWQ9Imljb24tZmlsZS10ZXh0MiIgdmlld2JveD0iMCAwIDMyIDMyIj4KPHBhdGggZD0iTTI4LjY4MSA3LjE1OWMtMC42OTQtMC45NDctMS42NjItMi4wNTMtMi43MjQtMy4xMTZzLTIuMTY5LTIuMDMwLTMuMTE2LTIuNzI0Yy0xLjYxMi0xLjE4Mi0yLjM5My0xLjMxOS0yLjg0MS0xLjMxOWgtMTUuNWMtMS4zNzggMC0yLjUgMS4xMjEtMi41IDIuNXYyN2MwIDEuMzc4IDEuMTIyIDIuNSAyLjUgMi41aDIzYzEuMzc4IDAgMi41LTEuMTIyIDIuNS0yLjV2LTE5LjVjMC0wLjQ0OC0wLjEzNy0xLjIzLTEuMzE5LTIuODQxek0yNC41NDMgNS40NTdjMC45NTkgMC45NTkgMS43MTIgMS44MjUgMi4yNjggMi41NDNoLTQuODExdi00LjgxMWMwLjcxOCAwLjU1NiAxLjU4NCAxLjMwOSAyLjU0MyAyLjI2OHpNMjggMjkuNWMwIDAuMjcxLTAuMjI5IDAuNS0wLjUgMC41aC0yM2MtMC4yNzEgMC0wLjUtMC4yMjktMC41LTAuNXYtMjdjMC0wLjI3MSAwLjIyOS0wLjUgMC41LTAuNSAwIDAgMTUuNDk5LTAgMTUuNSAwdjdjMCAwLjU1MiAwLjQ0OCAxIDEgMWg3djE5LjV6IiAvPgo8cGF0aCBkPSJNMjMgMjZoLTE0Yy0wLjU1MiAwLTEtMC40NDgtMS0xczAuNDQ4LTEgMS0xaDE0YzAuNTUyIDAgMSAwLjQ0OCAxIDFzLTAuNDQ4IDEtMSAxeiIgLz4KPHBhdGggZD0iTTIzIDIyaC0xNGMtMC41NTIgMC0xLTAuNDQ4LTEtMXMwLjQ0OC0xIDEtMWgxNGMwLjU1MiAwIDEgMC40NDggMSAxcy0wLjQ0OCAxLTEgMXoiIC8+CjxwYXRoIGQ9Ik0yMyAxOGgtMTRjLTAuNTUyIDAtMS0wLjQ0OC0xLTFzMC40NDgtMSAxLTFoMTRjMC41NTIgMCAxIDAuNDQ4IDEgMXMtMC40NDggMS0xIDF6IiAvPgo8L3N5bWJvbD4KPC9kZWZzPgo8L3N2Zz4=)

``` xr-text-repr-fallback
<xarray.Dataset> Size: 413kB
Dimensions:  (x: 102, y: 72)
Coordinates:
  * x        (x) float64 816B 6.796e+05 6.796e+05 ... 6.806e+05 6.806e+05
  * y        (y) float64 576B 5.152e+06 5.152e+06 ... 5.151e+06 5.151e+06
Data variables: (12/14)
    VH_min   (y, x) float32 29kB 0.02674 0.03061 0.02567 ... 0.0006829 0.004903
    VH_max   (y, x) float32 29kB 0.3667 0.2318 0.3059 ... 0.3418 0.3337 0.3239
    VH_mean  (y, x) float32 29kB 0.1429 0.115 0.1543 ... 0.06667 0.06222 0.06416
    VH_sd    (y, x) float32 29kB 0.1133 0.06834 0.1001 ... 0.1083 0.1061 0.09657
    VH_q10   (y, x) float32 29kB 0.03353 0.0385 0.03229 ... 0.001945 0.007251
    VH_q50   (y, x) float32 29kB 0.1021 0.1019 0.1477 ... 0.005219 0.01378
    ...       ...
    VV_max   (y, x) float32 29kB 1.049 0.8286 1.335 2.946 ... 2.422 2.065 1.579
    VV_mean  (y, x) float32 29kB 0.4665 0.539 0.8925 ... 0.4588 0.4244 0.4193
    VV_sd    (y, x) float32 29kB 0.2784 0.1475 0.3444 ... 0.7121 0.6607 0.593
    VV_q10   (y, x) float32 29kB 0.2126 0.3474 0.4901 ... 0.01284 0.02607
    VV_q50   (y, x) float32 29kB 0.3489 0.5193 0.9696 ... 0.04894 0.0215 0.04818
    VV_q90   (y, x) float32 29kB 0.9063 0.6914 1.309 2.694 ... 1.286 1.305 1.391
Attributes:
    Conventions:  CF-1.9
    institution:  Copernicus Data Space Ecosystem openEO API - 0.73.0a13.dev2...
    description:  
    title:        
```

xarray.Dataset

Dimensions:

- x: 102
- y: 72

Coordinates: (2)

x

\(x\)

float64

6.796e+05 6.796e+05 ... 6.806e+05

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
projection_x_coordinate

long_name :  
x coordinate of projection

units :  
m

    array([679635., 679645., 679655., 679665., 679675., 679685., 679695., 679705.,
           679715., 679725., 679735., 679745., 679755., 679765., 679775., 679785.,
           679795., 679805., 679815., 679825., 679835., 679845., 679855., 679865.,
           679875., 679885., 679895., 679905., 679915., 679925., 679935., 679945.,
           679955., 679965., 679975., 679985., 679995., 680005., 680015., 680025.,
           680035., 680045., 680055., 680065., 680075., 680085., 680095., 680105.,
           680115., 680125., 680135., 680145., 680155., 680165., 680175., 680185.,
           680195., 680205., 680215., 680225., 680235., 680245., 680255., 680265.,
           680275., 680285., 680295., 680305., 680315., 680325., 680335., 680345.,
           680355., 680365., 680375., 680385., 680395., 680405., 680415., 680425.,
           680435., 680445., 680455., 680465., 680475., 680485., 680495., 680505.,
           680515., 680525., 680535., 680545., 680555., 680565., 680575., 680585.,
           680595., 680605., 680615., 680625., 680635., 680645.])

y

\(y\)

float64

5.152e+06 5.152e+06 ... 5.151e+06

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
projection_y_coordinate

long_name :  
y coordinate of projection

units :  
m

    array([5151615., 5151605., 5151595., 5151585., 5151575., 5151565., 5151555.,
           5151545., 5151535., 5151525., 5151515., 5151505., 5151495., 5151485.,
           5151475., 5151465., 5151455., 5151445., 5151435., 5151425., 5151415.,
           5151405., 5151395., 5151385., 5151375., 5151365., 5151355., 5151345.,
           5151335., 5151325., 5151315., 5151305., 5151295., 5151285., 5151275.,
           5151265., 5151255., 5151245., 5151235., 5151225., 5151215., 5151205.,
           5151195., 5151185., 5151175., 5151165., 5151155., 5151145., 5151135.,
           5151125., 5151115., 5151105., 5151095., 5151085., 5151075., 5151065.,
           5151055., 5151045., 5151035., 5151025., 5151015., 5151005., 5150995.,
           5150985., 5150975., 5150965., 5150955., 5150945., 5150935., 5150925.,
           5150915., 5150905.])

Data variables: (14)

VH_min

(y, x)

float32

0.02674 0.03061 ... 0.004903

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_min

units :  

grid_mapping :  
crs

    array([[0.02674182, 0.03060655, 0.02567101, ..., 0.00601044, 0.00778116,
            0.00501412],
           [0.02434754, 0.01943763, 0.02222876, ..., 0.00559112, 0.00838348,
            0.0070325 ],
           [0.02164285, 0.02079906, 0.01872039, ..., 0.01395037, 0.01381883,
            0.01567465],
           ...,
           [0.00795914, 0.00503796, 0.00608822, ..., 0.00031839, 0.00015682,
            0.00452761],
           [0.00796834, 0.00705737, 0.00658798, ..., 0.00277543, 0.00119612,
            0.00067009],
           [0.00856518, 0.00747212, 0.00880753, ..., 0.0048942 , 0.00068292,
            0.00490338]], dtype=float32)

VH_max

(y, x)

float32

0.3667 0.2318 ... 0.3337 0.3239

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_max

units :  

grid_mapping :  
crs

    array([[0.3666854 , 0.23177792, 0.3058646 , ..., 0.0439763 , 0.04094   ,
            0.02975207],
           [0.21195813, 0.22264814, 0.30923468, ..., 0.07654878, 0.0534571 ,
            0.04696089],
           [0.20157108, 0.13497874, 0.17935418, ..., 0.07292594, 0.05113525,
            0.10425825],
           ...,
           [0.04003721, 0.03628872, 0.03952755, ..., 0.23259598, 0.2580061 ,
            0.27623877],
           [0.03373394, 0.02419831, 0.04764988, ..., 0.33312795, 0.33749843,
            0.36123085],
           [0.02758772, 0.0249892 , 0.03029031, ..., 0.34179702, 0.3337454 ,
            0.32388407]], dtype=float32)

VH_mean

(y, x)

float32

0.1429 0.115 ... 0.06222 0.06416

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_mean

units :  

grid_mapping :  
crs

    array([[0.14288546, 0.11500914, 0.1542739 , ..., 0.02665137, 0.01882942,
            0.01449044],
           [0.09936215, 0.10387021, 0.14328857, ..., 0.02899301, 0.02413673,
            0.0235579 ],
           [0.09552318, 0.07660887, 0.08098979, ..., 0.03156895, 0.03469853,
            0.04495636],
           ...,
           [0.02376825, 0.02101665, 0.01800491, ..., 0.06174954, 0.06418014,
            0.07215327],
           [0.01827349, 0.01482338, 0.01564552, ..., 0.06816787, 0.06432707,
            0.06720016],
           [0.01598492, 0.01483757, 0.01873437, ..., 0.06667353, 0.0622225 ,
            0.06415994]], dtype=float32)

VH_sd

(y, x)

float32

0.1133 0.06834 ... 0.1061 0.09657

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_sd

units :  

grid_mapping :  
crs

    array([[0.11326765, 0.06834466, 0.100072  , ..., 0.01225379, 0.00961442,
            0.00768412],
           [0.06348489, 0.06585505, 0.1056164 , ..., 0.01743488, 0.01358465,
            0.01294326],
           [0.05166667, 0.03636026, 0.04513597, ..., 0.01570882, 0.01219403,
            0.02381209],
           ...,
           [0.00898491, 0.00823746, 0.00930954, ..., 0.0841855 , 0.09135819,
            0.08867288],
           [0.00716817, 0.0061248 , 0.01017574, ..., 0.10467196, 0.10538495,
            0.10317834],
           [0.00546202, 0.00567765, 0.00694082, ..., 0.10834996, 0.10610394,
            0.09657337]], dtype=float32)

VH_q10

(y, x)

float32

0.03353 0.0385 ... 0.007251

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_q10

units :  

grid_mapping :  
crs

    array([[0.03353042, 0.03850244, 0.03228896, ..., 0.00999628, 0.0090665 ,
            0.0063625 ],
           [0.03058114, 0.03268816, 0.03500263, ..., 0.01178256, 0.01240073,
            0.0118051 ],
           [0.0348209 , 0.0259043 , 0.0312931 , ..., 0.01518946, 0.01893369,
            0.02146387],
           ...,
           [0.01186323, 0.01226142, 0.0081033 , ..., 0.00176324, 0.00373246,
            0.01022064],
           [0.00930115, 0.00779835, 0.00810983, ..., 0.0059328 , 0.00201939,
            0.00809731],
           [0.01025093, 0.00794533, 0.01099781, ..., 0.00728927, 0.00194547,
            0.00725082]], dtype=float32)

VH_q50

(y, x)

float32

0.1021 0.1019 ... 0.005219 0.01378

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_q50

units :  

grid_mapping :  
crs

    array([[0.10211158, 0.1019193 , 0.14772725, ..., 0.02832318, 0.01862846,
            0.01214658],
           [0.08645285, 0.09305815, 0.15053682, ..., 0.02688267, 0.02116134,
            0.01902985],
           [0.09481071, 0.08545977, 0.07932476, ..., 0.02895101, 0.03637188,
            0.03904133],
           ...,
           [0.02471455, 0.02156118, 0.01542514, ..., 0.00869222, 0.00739777,
            0.02117217],
           [0.01880951, 0.01355901, 0.01245657, ..., 0.00900793, 0.00728122,
            0.01722938],
           [0.01388785, 0.01467958, 0.01659229, ..., 0.01092308, 0.00521852,
            0.01378132]], dtype=float32)

VH_q90

(y, x)

float32

0.2987 0.215 ... 0.2179 0.1921

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_q90

units :  

grid_mapping :  
crs

    array([[0.29867756, 0.21499813, 0.28266963, ..., 0.04046655, 0.03015675,
            0.026499  ],
           [0.19474691, 0.19185518, 0.29532525, ..., 0.0421317 , 0.04530496,
            0.04015889],
           [0.16524318, 0.11452919, 0.1298617 , ..., 0.04846318, 0.04770849,
            0.07075449],
           ...,
           [0.03293557, 0.02840455, 0.03003761, ..., 0.18306498, 0.1981852 ,
            0.20082626],
           [0.0245586 , 0.02267605, 0.02323536, ..., 0.22076672, 0.21559213,
            0.19790171],
           [0.02199888, 0.02201751, 0.02875963, ..., 0.23092027, 0.21794802,
            0.19206661]], dtype=float32)

VV_min

(y, x)

float32

0.1402 0.2987 ... 0.007998 0.01725

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_min

units :  

grid_mapping :  
crs

    array([[0.14019679, 0.29865152, 0.28363422, ..., 0.06331535, 0.03262557,
            0.01858132],
           [0.16940908, 0.31863624, 0.24485376, ..., 0.07898029, 0.03525665,
            0.02794796],
           [0.24082465, 0.28383112, 0.24884047, ..., 0.09419372, 0.03557625,
            0.0369344 ],
           ...,
           [0.04434901, 0.05066326, 0.0458343 , ..., 0.01240802, 0.00370447,
            0.02267214],
           [0.03579092, 0.04549251, 0.04555964, ..., 0.01389879, 0.00963537,
            0.02748128],
           [0.03958815, 0.03769322, 0.03675687, ..., 0.02074386, 0.0079982 ,
            0.01724508]], dtype=float32)

VV_max

(y, x)

float32

1.049 0.8286 1.335 ... 2.065 1.579

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_max

units :  

grid_mapping :  
crs

    array([[1.0493535 , 0.82862014, 1.3347877 , ..., 0.25439578, 0.1374378 ,
            0.09287846],
           [0.72565496, 0.96587086, 1.2862892 , ..., 0.23207396, 0.13379517,
            0.11052042],
           [0.7708433 , 0.724252  , 0.92534196, ..., 0.3143082 , 0.24172042,
            0.19969708],
           ...,
           [0.18325597, 0.1907593 , 0.29473734, ..., 1.6887966 , 2.0245907 ,
            2.1313047 ],
           [0.1463719 , 0.2585449 , 0.27819204, ..., 2.6331792 , 2.714679  ,
            2.5341723 ],
           [0.29118454, 0.36602065, 0.37356612, ..., 2.4218872 , 2.0654576 ,
            1.5792611 ]], dtype=float32)

VV_mean

(y, x)

float32

0.4665 0.539 ... 0.4244 0.4193

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_mean

units :  

grid_mapping :  
crs

    array([[0.46648738, 0.53899664, 0.8925202 , ..., 0.13969284, 0.0759951 ,
            0.05299051],
           [0.45733884, 0.49542317, 0.56161284, ..., 0.14232773, 0.0816595 ,
            0.06533601],
           [0.49459115, 0.4776926 , 0.50387233, ..., 0.15782706, 0.10720854,
            0.11489608],
           ...,
           [0.10469471, 0.10448772, 0.11769362, ..., 0.31995645, 0.3485685 ,
            0.3862137 ],
           [0.07841541, 0.09408469, 0.10966484, ..., 0.41748032, 0.4250287 ,
            0.45460498],
           [0.11616257, 0.10161167, 0.10746226, ..., 0.4588026 , 0.42443722,
            0.41931656]], dtype=float32)

VV_sd

(y, x)

float32

0.2784 0.1475 ... 0.6607 0.593

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_sd

units :  

grid_mapping :  
crs

    array([[0.27841237, 0.14745179, 0.34437087, ..., 0.06012796, 0.02991889,
            0.02088385],
           [0.16951475, 0.17175552, 0.26635963, ..., 0.04731377, 0.03447982,
            0.02140912],
           [0.17129715, 0.13476618, 0.1936407 , ..., 0.06078154, 0.05113195,
            0.04449951],
           ...,
           [0.04057432, 0.03630581, 0.06312171, ..., 0.5146163 , 0.59392166,
            0.5953689 ],
           [0.0369882 , 0.05282037, 0.06334678, ..., 0.7285251 , 0.7573787 ,
            0.71854514],
           [0.06417554, 0.07890163, 0.08239751, ..., 0.71209246, 0.66065097,
            0.5929938 ]], dtype=float32)

VV_q10

(y, x)

float32

0.2126 0.3474 ... 0.01284 0.02607

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_q10

units :  

grid_mapping :  
crs

    array([[0.21261172, 0.34743842, 0.49005735, ..., 0.08692311, 0.04234186,
            0.03029387],
           [0.27373675, 0.3255348 , 0.32698345, ..., 0.0881958 , 0.04158782,
            0.04459156],
           [0.31633413, 0.33494526, 0.30596238, ..., 0.10867397, 0.050297  ,
            0.05588451],
           ...,
           [0.06260646, 0.07090059, 0.05708602, ..., 0.02009165, 0.01006144,
            0.04484886],
           [0.04793053, 0.05190809, 0.04691131, ..., 0.02068214, 0.01119935,
            0.03875778],
           [0.04816738, 0.05794685, 0.05891509, ..., 0.02165532, 0.01283511,
            0.02606884]], dtype=float32)

VV_q50

(y, x)

float32

0.3489 0.5193 ... 0.0215 0.04818

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_q50

units :  

grid_mapping :  
crs

    array([[0.3488692 , 0.5192621 , 0.969603  , ..., 0.12270404, 0.07250372,
            0.04695785],
           [0.44175318, 0.4679004 , 0.5149218 , ..., 0.1301802 , 0.07635964,
            0.06538481],
           [0.4275158 , 0.4543993 , 0.48266268, ..., 0.14400242, 0.10413335,
            0.12262902],
           ...,
           [0.0974353 , 0.09865014, 0.10969326, ..., 0.0393924 , 0.0395264 ,
            0.10231223],
           [0.06333554, 0.08768404, 0.10789572, ..., 0.03861215, 0.0284642 ,
            0.06759839],
           [0.10041548, 0.07786189, 0.08261804, ..., 0.04893823, 0.0215037 ,
            0.04818135]], dtype=float32)

VV_q90

(y, x)

float32

0.9063 0.6914 1.309 ... 1.305 1.391

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_q90

units :  

grid_mapping :  
crs

    array([[0.9063469 , 0.6913692 , 1.3087583 , ..., 0.23422815, 0.11266159,
            0.07735866],
           [0.69916624, 0.64584655, 0.85971904, ..., 0.20752184, 0.1306962 ,
            0.0891365 ],
           [0.7468773 , 0.65454054, 0.7554172 , ..., 0.24152495, 0.15977135,
            0.1656553 ],
           ...,
           [0.1680559 , 0.14842111, 0.17786023, ..., 1.0161972 , 1.0729179 ,
            1.0630019 ],
           [0.13973843, 0.13285719, 0.1529504 , ..., 1.1123298 , 1.1440662 ,
            1.2479637 ],
           [0.16913494, 0.13975853, 0.16091974, ..., 1.285539  , 1.3047844 ,
            1.3909923 ]], dtype=float32)

Indexes: (2)

x

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(Index([679635.0, 679645.0, 679655.0, 679665.0, 679675.0, 679685.0, 679695.0,
           679705.0, 679715.0, 679725.0,
           ...
           680555.0, 680565.0, 680575.0, 680585.0, 680595.0, 680605.0, 680615.0,
           680625.0, 680635.0, 680645.0],
          dtype='float64', name='x', length=102))

y

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(Index([5151615.0, 5151605.0, 5151595.0, 5151585.0, 5151575.0, 5151565.0,
           5151555.0, 5151545.0, 5151535.0, 5151525.0, 5151515.0, 5151505.0,
           5151495.0, 5151485.0, 5151475.0, 5151465.0, 5151455.0, 5151445.0,
           5151435.0, 5151425.0, 5151415.0, 5151405.0, 5151395.0, 5151385.0,
           5151375.0, 5151365.0, 5151355.0, 5151345.0, 5151335.0, 5151325.0,
           5151315.0, 5151305.0, 5151295.0, 5151285.0, 5151275.0, 5151265.0,
           5151255.0, 5151245.0, 5151235.0, 5151225.0, 5151215.0, 5151205.0,
           5151195.0, 5151185.0, 5151175.0, 5151165.0, 5151155.0, 5151145.0,
           5151135.0, 5151125.0, 5151115.0, 5151105.0, 5151095.0, 5151085.0,
           5151075.0, 5151065.0, 5151055.0, 5151045.0, 5151035.0, 5151025.0,
           5151015.0, 5151005.0, 5150995.0, 5150985.0, 5150975.0, 5150965.0,
           5150955.0, 5150945.0, 5150935.0, 5150925.0, 5150915.0, 5150905.0],
          dtype='float64', name='y'))

Attributes: (4)

Conventions :  
CF-1.9

institution :  
Copernicus Data Space Ecosystem openEO API - 0.73.0a13.dev20260622+3737

description :  

title :  

## Build S1 SAR stats UDP

Suppose we want to save the above-described algorithm as a User-Defined-Process(UDP). Therefore, in this section, we define the input parameters, define the earlier workflow and then save it as a process.

The only limitation of this approach, is that your workflow needs to be defined as a single process graph. So workflows that require multiple openEO invocations or complex parameter preprocessing won’t work yet. However, thanks to the flexibility of openEO and the ability to include custom code as a UDF, a lot of algorithms can already be defined in a single openEO graph.

``` python
import openeo
from openeo.api.process import Parameter
from openeo.processes import array_create, array_concat
```

Let us define the UDP parameters to allow specifying the spatio-temporal extent.

To make a service available to users, we might want to replace certain fixed values in your process graph with parameters that can be set by the user of your process. This provides you with a parameterised UDP.

``` python
temporal_extent = Parameter(
    name="temporal_extent",
    description="The time window to calculate the stats for.",
    schema={"type": "array", "subtype": "temporal-interval"},
    default=["2023-05-01", "2023-07-30"],
)
spatial_extent = Parameter(
    name="spatial_extent",
    description="The spatial extent to calculate the stats for.",
    schema={"type": "object", "subtype": "bounding-box"},
    default={"west": 8.82, "south": 44.40, "east": 8.92, "north": 44.45},
)
```

``` python
s1_raw = connection.load_collection(
    collection_id="SENTINEL1_GRD",
    temporal_extent=temporal_extent,
    spatial_extent=spatial_extent,
    bands=["VH", "VV"],
)
s1_raw = s1_raw.sar_backscatter(coefficient="sigma0-ellipsoid")

# Unlike above, where we defined the `apply_dimension` process
# through a regular python function, we do it here compactily with a single "lambda".
s1_stats = s1_raw.apply_dimension(
    process=lambda data: array_concat(
        array1=array_create([data.min(), data.max(), data.mean(), data.sd()]),
        array2=data.quantiles([0.1, 0.5, 0.9]),
    ),
    dimension="t",
    target_dimension="bands",
)
# Rename band labels, pairing original band names with stat names
s1_stats = s1_stats.rename_labels(
    "bands",
    [
        f"{b}_{s}"
        for b in s1_stats.metadata.band_names
        for s in ["min", "max", "mean", "sd", "q10", "q50", "q90"]
    ],
)
```

Store this parameterized data cube as a UDP

``` python
udp_sar = connection.save_user_defined_process(
    user_defined_process_id="s1_stats",
    process_graph=s1_stats,
    parameters=[temporal_extent, spatial_extent],
    summary="S1 SAR stats",
    description="Calculate S1 SAR stats (min, max, mean, sd, q10, q50, q90). This service can cost an approximate of 3-5 credits per sq km. This cost is based on resource consumpltion only and added-value cost has not been included.",
    public=True,
)
```

    Preflight process graph validation raised: [UpstreamValidationInfo] Backend 'cdse' reported validation errors [ProcessParameterRequired] Process 'n/a' parameter 'spatial_extent' is required.

When saving a process, please note that saved processes are private by default, nonetheless can be used multiple times by an individual. Therefore, to share with a large audience, you will need a public URL that can be achieved once the process is saved as public.

## Use the saved UDP in the Python Client

Now, let’s evaluate our freshly created user-defined processes “s1_stats”. We can use `datacube_from_process()` to create a DataCube from this process and only have to provide concrete temporal and spatial extents

Note: Since the `spatial_extent` and `temporal_extent` variable were re-assigned as a paramter definition, you might have lost their value, so please don’t forget to re-define your interested extent in the cell below.

``` python
sar = connection.datacube_from_process(
    "s1_stats",
    namespace=public_url,
    temporal_extent=["2023-05-01", "2023-07-30"],
    spatial_extent={"west": 8.82, "south": 44.40, "east": 8.92, "north": 44.45},
)
```

``` python
sar.download("sar_udp.nc")
```

``` python
ds = xarray.load_dataset("sar_udp.nc").drop_vars("crs")
ds
```

    sh: line 1: getfattr: command not found

![](data:image/svg+xml;base64,PHN2ZyBzdHlsZT0icG9zaXRpb246IGFic29sdXRlOyB3aWR0aDogMDsgaGVpZ2h0OiAwOyBvdmVyZmxvdzogaGlkZGVuIj4KPGRlZnM+CjxzeW1ib2wgaWQ9Imljb24tZGF0YWJhc2UiIHZpZXdib3g9IjAgMCAzMiAzMiI+CjxwYXRoIGQ9Ik0xNiAwYy04LjgzNyAwLTE2IDIuMjM5LTE2IDV2NGMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di00YzAtMi43NjEtNy4xNjMtNS0xNi01eiIgLz4KPHBhdGggZD0iTTE2IDE3Yy04LjgzNyAwLTE2LTIuMjM5LTE2LTV2NmMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di02YzAgMi43NjEtNy4xNjMgNS0xNiA1eiIgLz4KPHBhdGggZD0iTTE2IDI2Yy04LjgzNyAwLTE2LTIuMjM5LTE2LTV2NmMwIDIuNzYxIDcuMTYzIDUgMTYgNXMxNi0yLjIzOSAxNi01di02YzAgMi43NjEtNy4xNjMgNS0xNiA1eiIgLz4KPC9zeW1ib2w+CjxzeW1ib2wgaWQ9Imljb24tZmlsZS10ZXh0MiIgdmlld2JveD0iMCAwIDMyIDMyIj4KPHBhdGggZD0iTTI4LjY4MSA3LjE1OWMtMC42OTQtMC45NDctMS42NjItMi4wNTMtMi43MjQtMy4xMTZzLTIuMTY5LTIuMDMwLTMuMTE2LTIuNzI0Yy0xLjYxMi0xLjE4Mi0yLjM5My0xLjMxOS0yLjg0MS0xLjMxOWgtMTUuNWMtMS4zNzggMC0yLjUgMS4xMjEtMi41IDIuNXYyN2MwIDEuMzc4IDEuMTIyIDIuNSAyLjUgMi41aDIzYzEuMzc4IDAgMi41LTEuMTIyIDIuNS0yLjV2LTE5LjVjMC0wLjQ0OC0wLjEzNy0xLjIzLTEuMzE5LTIuODQxek0yNC41NDMgNS40NTdjMC45NTkgMC45NTkgMS43MTIgMS44MjUgMi4yNjggMi41NDNoLTQuODExdi00LjgxMWMwLjcxOCAwLjU1NiAxLjU4NCAxLjMwOSAyLjU0MyAyLjI2OHpNMjggMjkuNWMwIDAuMjcxLTAuMjI5IDAuNS0wLjUgMC41aC0yM2MtMC4yNzEgMC0wLjUtMC4yMjktMC41LTAuNXYtMjdjMC0wLjI3MSAwLjIyOS0wLjUgMC41LTAuNSAwIDAgMTUuNDk5LTAgMTUuNSAwdjdjMCAwLjU1MiAwLjQ0OCAxIDEgMWg3djE5LjV6IiAvPgo8cGF0aCBkPSJNMjMgMjZoLTE0Yy0wLjU1MiAwLTEtMC40NDgtMS0xczAuNDQ4LTEgMS0xaDE0YzAuNTUyIDAgMSAwLjQ0OCAxIDFzLTAuNDQ4IDEtMSAxeiIgLz4KPHBhdGggZD0iTTIzIDIyaC0xNGMtMC41NTIgMC0xLTAuNDQ4LTEtMXMwLjQ0OC0xIDEtMWgxNGMwLjU1MiAwIDEgMC40NDggMSAxcy0wLjQ0OCAxLTEgMXoiIC8+CjxwYXRoIGQ9Ik0yMyAxOGgtMTRjLTAuNTUyIDAtMS0wLjQ0OC0xLTFzMC40NDgtMSAxLTFoMTRjMC41NTIgMCAxIDAuNDQ4IDEgMXMtMC40NDggMS0xIDF6IiAvPgo8L3N5bWJvbD4KPC9kZWZzPgo8L3N2Zz4=)

``` xr-text-repr-fallback
<xarray.Dataset> Size: 25MB
Dimensions:  (x: 798, y: 558)
Coordinates:
  * x        (x) float64 6kB 4.857e+05 4.857e+05 ... 4.936e+05 4.936e+05
  * y        (y) float64 4kB 4.922e+06 4.922e+06 ... 4.916e+06 4.916e+06
Data variables: (12/14)
    VH_min   (y, x) float32 2MB 0.005179 0.0006744 ... 0.0002321 0.0003233
    VH_max   (y, x) float32 2MB 0.0437 0.0614 0.08774 ... 0.1194 0.0495 0.0811
    VH_mean  (y, x) float32 2MB 0.01742 0.01655 0.02166 ... 0.004266 0.005588
    VH_sd    (y, x) float32 2MB 0.009777 0.01646 0.02353 ... 0.009046 0.01441
    VH_q10   (y, x) float32 2MB 0.008391 0.002142 ... 0.0004121 0.000853
    VH_q50   (y, x) float32 2MB 0.01468 0.01079 0.01708 ... 0.001963 0.002638
    ...       ...
    VV_max   (y, x) float32 2MB 0.2511 0.3178 0.4048 ... 1.687 0.2311 0.05796
    VV_mean  (y, x) float32 2MB 0.07481 0.06502 0.07854 ... 0.02349 0.02043
    VV_sd    (y, x) float32 2MB 0.04468 0.06506 0.08718 ... 0.0407 0.01377
    VV_q10   (y, x) float32 2MB 0.0343 0.01257 0.006335 ... 0.005751 0.007017
    VV_q50   (y, x) float32 2MB 0.06718 0.03864 0.04281 ... 0.01496 0.01626
    VV_q90   (y, x) float32 2MB 0.113 0.1201 0.1538 ... 0.03544 0.03565 0.03735
Attributes:
    Conventions:  CF-1.9
    institution:  openEO platform
```

xarray.Dataset

Dimensions:

- x: 798
- y: 558

Coordinates: (2)

x

\(x\)

float64

4.857e+05 4.857e+05 ... 4.936e+05

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
projection_x_coordinate

long_name :  
x coordinate of projection

units :  
m

    array([485665., 485675., 485685., ..., 493615., 493625., 493635.])

y

\(y\)

float64

4.922e+06 4.922e+06 ... 4.916e+06

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

standard_name :  
projection_y_coordinate

long_name :  
y coordinate of projection

units :  
m

    array([4921875., 4921865., 4921855., ..., 4916325., 4916315., 4916305.])

Data variables: (14)

VH_min

(y, x)

float32

0.005179 0.0006744 ... 0.0003233

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_min

units :  

grid_mapping :  
crs

    array([[5.1790150e-03, 6.7435059e-04, 3.5491666e-05, ..., 1.4843310e-03,
            6.5751430e-03, 8.2683116e-03],
           [2.6808402e-03, 6.8866118e-04, 4.7362540e-04, ..., 7.0360961e-04,
            4.6409522e-03, 1.2251703e-02],
           [1.6895927e-03, 5.7533314e-04, 6.1662577e-04, ..., 2.5348314e-03,
            2.8690544e-03, 1.3530747e-02],
           ...,
           [5.2149335e-06, 1.3619781e-05, 4.2276206e-06, ..., 3.1443514e-04,
            6.1937229e-05, 6.9807669e-05],
           [1.0691515e-05, 7.4738605e-06, 6.8401428e-06, ..., 4.2155088e-04,
            3.6849501e-04, 7.0850976e-05],
           [2.8010245e-06, 1.2153989e-06, 2.1162425e-05, ..., 5.4035721e-05,
            2.3213204e-04, 3.2328154e-04]], dtype=float32)

VH_max

(y, x)

float32

0.0437 0.0614 ... 0.0495 0.0811

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_max

units :  

grid_mapping :  
crs

    array([[0.04369812, 0.06139704, 0.08773565, ..., 0.29503146, 0.23575717,
            0.10494611],
           [0.07613949, 0.10430614, 0.13548432, ..., 0.21424744, 0.12483119,
            0.07347236],
           [0.1064273 , 0.12625267, 0.1408355 , ..., 0.16185929, 0.11942944,
            0.08524383],
           ...,
           [0.0054121 , 0.00664679, 0.00421263, ..., 0.07956106, 0.0891263 ,
            0.07002673],
           [0.003332  , 0.00606422, 0.00471943, ..., 0.09593336, 0.0576453 ,
            0.06981783],
           [0.00481099, 0.00488732, 0.0039305 , ..., 0.11942604, 0.04950251,
            0.08110013]], dtype=float32)

VH_mean

(y, x)

float32

0.01742 0.01655 ... 0.005588

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_mean

units :  

grid_mapping :  
crs

    array([[0.01741548, 0.01655145, 0.02166374, ..., 0.06092047, 0.05539886,
            0.03781578],
           [0.01671887, 0.02131754, 0.02888809, ..., 0.06094961, 0.04995695,
            0.03515729],
           [0.02092094, 0.02824179, 0.03675164, ..., 0.05068799, 0.04236713,
            0.03358325],
           ...,
           [0.00125552, 0.00162496, 0.0016311 , ..., 0.00644752, 0.00565294,
            0.00463481],
           [0.00119254, 0.00124422, 0.00126841, ..., 0.0073044 , 0.00508048,
            0.00489696],
           [0.00172758, 0.0013916 , 0.00107616, ..., 0.0068505 , 0.00426559,
            0.00558802]], dtype=float32)

VH_sd

(y, x)

float32

0.009777 0.01646 ... 0.01441

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_sd

units :  

grid_mapping :  
crs

    array([[0.00977687, 0.0164646 , 0.02353494, ..., 0.07095637, 0.05595946,
            0.02619051],
           [0.01536347, 0.02411691, 0.03456507, ..., 0.06206268, 0.04097066,
            0.01728314],
           [0.02447785, 0.03241063, 0.04142125, ..., 0.04792081, 0.03154533,
            0.01647938],
           ...,
           [0.00114314, 0.00137188, 0.0011653 , ..., 0.01467543, 0.01591976,
            0.01265947],
           [0.00088183, 0.00122855, 0.00129493, ..., 0.01803518, 0.01054358,
            0.01262773],
           [0.0015041 , 0.00136845, 0.00095486, ..., 0.02155257, 0.00904604,
            0.01440865]], dtype=float32)

VH_q10

(y, x)

float32

0.008391 0.002142 ... 0.000853

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_q10

units :  

grid_mapping :  
crs

    array([[8.3911344e-03, 2.1424016e-03, 2.3070923e-03, ..., 3.6896435e-03,
            7.8630270e-03, 1.1912103e-02],
           [4.3198224e-03, 1.4414280e-03, 1.1491117e-03, ..., 2.9722620e-03,
            8.5382750e-03, 1.5247992e-02],
           [2.7094425e-03, 2.1519477e-03, 1.5253305e-03, ..., 5.4725041e-03,
            1.3184761e-02, 1.6802395e-02],
           ...,
           [1.8675165e-04, 4.9796078e-04, 1.7651130e-04, ..., 9.6274621e-04,
            4.0755581e-04, 5.7852990e-04],
           [1.1161680e-04, 1.3260319e-04, 1.4015246e-04, ..., 7.1107986e-04,
            9.8702637e-04, 2.8157691e-04],
           [1.7756959e-04, 5.7891462e-05, 9.7337863e-05, ..., 9.8372204e-04,
            4.1209668e-04, 8.5302879e-04]], dtype=float32)

VH_q50

(y, x)

float32

0.01468 0.01079 ... 0.002638

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_q50

units :  

grid_mapping :  
crs

    array([[0.01468267, 0.01079342, 0.01708473, ..., 0.01948099, 0.02511071,
            0.03023804],
           [0.01263583, 0.01671381, 0.01445456, ..., 0.02617684, 0.03053429,
            0.03173785],
           [0.00794464, 0.01316131, 0.01624785, ..., 0.0285993 , 0.02525841,
            0.02988026],
           ...,
           [0.00112736, 0.00113136, 0.00172897, ..., 0.00314602, 0.00232967,
            0.00223056],
           [0.00098514, 0.0009467 , 0.00079053, ..., 0.00256502, 0.00234279,
            0.00244587],
           [0.00126289, 0.0006234 , 0.00078776, ..., 0.00168159, 0.00196348,
            0.0026382 ]], dtype=float32)

VH_q90

(y, x)

float32

0.03195 0.03547 ... 0.006035

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VH_q90

units :  

grid_mapping :  
crs

    array([[0.03195012, 0.03546856, 0.04195141, ..., 0.13144307, 0.11525625,
            0.07022735],
           [0.03509531, 0.05296517, 0.07517841, ..., 0.13203068, 0.0990926 ,
            0.05953676],
           [0.04749506, 0.0683267 , 0.08865102, ..., 0.10454184, 0.08601395,
            0.05255165],
           ...,
           [0.00223277, 0.0032354 , 0.00339026, ..., 0.00647877, 0.00555456,
            0.00485078],
           [0.00247719, 0.0023786 , 0.00295119, ..., 0.00651465, 0.00635541,
            0.00559724],
           [0.00406873, 0.00309753, 0.00230574, ..., 0.00634639, 0.00551407,
            0.00603464]], dtype=float32)

VV_min

(y, x)

float32

0.02391 0.005213 ... 0.004197

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_min

units :  

grid_mapping :  
crs

    array([[0.02390507, 0.00521277, 0.00404566, ..., 0.01073809, 0.01970434,
            0.04344405],
           [0.01335756, 0.00581965, 0.00225224, ..., 0.01661292, 0.019276  ,
            0.03547296],
           [0.00724073, 0.00448705, 0.00288456, ..., 0.0120812 , 0.02887361,
            0.03648873],
           ...,
           [0.00058921, 0.00042484, 0.00086914, ..., 0.00373092, 0.00325532,
            0.00280475],
           [0.00050547, 0.0005377 , 0.0012994 , ..., 0.0022422 , 0.00110214,
            0.00271663],
           [0.00039152, 0.00049753, 0.00123949, ..., 0.00250965, 0.00194878,
            0.00419681]], dtype=float32)

VV_max

(y, x)

float32

0.2511 0.3178 ... 0.2311 0.05796

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_max

units :  

grid_mapping :  
crs

    array([[0.25112742, 0.31777614, 0.4047884 , ..., 0.7809679 , 0.7363567 ,
            0.47340414],
           [0.2294258 , 0.31974527, 0.44147012, ..., 0.76368874, 0.67648566,
            0.40874177],
           [0.26340145, 0.3639898 , 0.5107174 , ..., 0.75768167, 0.63088334,
            0.3060644 ],
           ...,
           [0.02670128, 0.02142781, 0.02463174, ..., 0.13321447, 0.12495995,
            0.10285159],
           [0.03128415, 0.01972793, 0.0268227 , ..., 0.7568402 , 0.13538426,
            0.04758164],
           [0.02613304, 0.02938594, 0.02403203, ..., 1.6866078 , 0.23107743,
            0.05796338]], dtype=float32)

VV_mean

(y, x)

float32

0.07481 0.06502 ... 0.02349 0.02043

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_mean

units :  

grid_mapping :  
crs

    array([[0.07481217, 0.0650217 , 0.07854302, ..., 0.24052969, 0.23712713,
            0.18436556],
           [0.0639153 , 0.07567065, 0.10576686, ..., 0.26281   , 0.22954036,
            0.15893254],
           [0.07485904, 0.09993037, 0.14651379, ..., 0.2439552 , 0.2082663 ,
            0.15894765],
           ...,
           [0.00674983, 0.00599584, 0.00619983, ..., 0.02454171, 0.02304699,
            0.02160381],
           [0.00705473, 0.00620282, 0.00637595, ..., 0.04153206, 0.0205185 ,
            0.01969542],
           [0.00671834, 0.00678353, 0.0067207 , ..., 0.07232488, 0.02349177,
            0.02042829]], dtype=float32)

VV_sd

(y, x)

float32

0.04468 0.06506 ... 0.0407 0.01377

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_sd

units :  

grid_mapping :  
crs

    array([[0.04467699, 0.0650629 , 0.08718428, ..., 0.24212098, 0.22354597,
            0.1375417 ],
           [0.05274361, 0.07710483, 0.11632709, ..., 0.26233742, 0.20125628,
            0.10303202],
           [0.07868785, 0.11076809, 0.16625147, ..., 0.24707831, 0.17260341,
            0.08196335],
           ...,
           [0.00609069, 0.00545064, 0.00566327, ..., 0.03062076, 0.02194226,
            0.01801645],
           [0.00640967, 0.00465139, 0.00536858, ..., 0.13562985, 0.02469136,
            0.0127027 ],
           [0.00594661, 0.00568424, 0.00463514, ..., 0.30508226, 0.04070332,
            0.01377046]], dtype=float32)

VV_q10

(y, x)

float32

0.0343 0.01257 ... 0.007017

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_q10

units :  

grid_mapping :  
crs

    array([[0.03430496, 0.01256511, 0.00633504, ..., 0.01995801, 0.0316762 ,
            0.0487122 ],
           [0.01507588, 0.00823221, 0.00616359, ..., 0.02197921, 0.03716285,
            0.05351951],
           [0.00887945, 0.00646014, 0.00581567, ..., 0.02167627, 0.04302126,
            0.05518135],
           ...,
           [0.00182068, 0.00159823, 0.00143851, ..., 0.00497847, 0.00796662,
            0.00665838],
           [0.00166041, 0.00206962, 0.00220824, ..., 0.0045406 , 0.00547958,
            0.00432789],
           [0.00175499, 0.00223989, 0.00232416, ..., 0.00385345, 0.00575079,
            0.00701721]], dtype=float32)

VV_q50

(y, x)

float32

0.06718 0.03864 ... 0.01496 0.01626

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_q50

units :  

grid_mapping :  
crs

    array([[0.06717545, 0.03863911, 0.0428113 , ..., 0.12390707, 0.1333968 ,
            0.11266621],
           [0.0514466 , 0.04761094, 0.05935188, ..., 0.13716178, 0.14292823,
            0.13210353],
           [0.03065991, 0.0265301 , 0.03832125, ..., 0.08813316, 0.13120368,
            0.13690317],
           ...,
           [0.00474584, 0.00396075, 0.00485182, ..., 0.01903854, 0.01967191,
            0.01795328],
           [0.0051854 , 0.00483886, 0.00442317, ..., 0.0164674 , 0.01324176,
            0.01717496],
           [0.00571051, 0.00461331, 0.00541438, ..., 0.01450604, 0.01496293,
            0.01626071]], dtype=float32)

VV_q90

(y, x)

float32

0.113 0.1201 ... 0.03565 0.03735

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWZpbGUtdGV4dDIiPjx1c2UgaHJlZj0iI2ljb24tZmlsZS10ZXh0MiIgLz48L3N2Zz4=)

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

long_name :  
VV_q90

units :  

grid_mapping :  
crs

    array([[0.11303069, 0.12011835, 0.15379867, ..., 0.5399144 , 0.5564473 ,
            0.38504428],
           [0.13325769, 0.16899867, 0.24364921, ..., 0.60198945, 0.49766067,
            0.34298924],
           [0.19181928, 0.24064352, 0.4064072 , ..., 0.5966895 , 0.39402968,
            0.27405775],
           ...,
           [0.01432398, 0.01624354, 0.01274676, ..., 0.03367758, 0.03424421,
            0.03272589],
           [0.0139405 , 0.0114498 , 0.01192626, ..., 0.0323368 , 0.03275811,
            0.03861197],
           [0.01121384, 0.0127006 , 0.01155272, ..., 0.03543746, 0.03564724,
            0.03735264]], dtype=float32)

Indexes: (2)

x

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(Index([485665.0, 485675.0, 485685.0, 485695.0, 485705.0, 485715.0, 485725.0,
           485735.0, 485745.0, 485755.0,
           ...
           493545.0, 493555.0, 493565.0, 493575.0, 493585.0, 493595.0, 493605.0,
           493615.0, 493625.0, 493635.0],
          dtype='float64', name='x', length=798))

y

PandasIndex

![](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiB4ci1pY29uLWRhdGFiYXNlIj48dXNlIGhyZWY9IiNpY29uLWRhdGFiYXNlIiAvPjwvc3ZnPg==)

    PandasIndex(Index([4921875.0, 4921865.0, 4921855.0, 4921845.0, 4921835.0, 4921825.0,
           4921815.0, 4921805.0, 4921795.0, 4921785.0,
           ...
           4916395.0, 4916385.0, 4916375.0, 4916365.0, 4916355.0, 4916345.0,
           4916335.0, 4916325.0, 4916315.0, 4916305.0],
          dtype='float64', name='y', length=558))

Attributes: (2)

Conventions :  
CF-1.9

institution :  
openEO platform

## Publishing your service online

Once the UDP defined above is saved within the openEO platform, a user also has the option to add this service to the openEO Marketplace. To register a User Defined Process (UDP), you must have a public URL for your service. You’ll also need to provide the saved process ID, which can be located within the public URL.

A detailed documentation on the process can be followed here: <https://documentation.dataspace.copernicus.eu/Applications/PlazaDetails/ManageService.html#register-and-publish-your-service>

# Credit Usage

Every openEO user is provided with a specific amount of credits. It’s important to understand that examining data, processes, or creating process graphs like UDP doesn’t cost any credits. However, executing these operations (synchronous or batch) which requires authentication does consume credits based on:

- CPU usage (measured in cores per second)
- Memory usage (measured in gigabytes per second)
- Storage usage (measured in gigabytes per day)
- Accessing data from specific layers (e.g., Sentinel Hub or commercial sources)
- Additional costs may apply if there’s value-added content, typically provided by third-party services like ‘s1_stats.’ For this reason, when publishing such services online, it’s advisable to include information about their credit consumption in the service description.

You can estimate the credits your service might use by reviewing the job information in the web editor.

With refernce to the documentation available [here](https://docs.openeo.cloud/federation/accounting.html#platform-credit-rates), you can calculate the possible service usage per square kilometer. Suppose, in my case, for 1 square kilometer, it amounted to 2273 CPU seconds and 5,457,138 megabytes-seconds, equivalent to approximately 0.9 and 1.45 credits, respectively. Hence, the total credits consumed by this process come to approximately 2.35 credits.

Back to top
