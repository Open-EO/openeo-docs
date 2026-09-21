# General Operations

General operations are reusable building blocks for calculations, comparisons, logic, arrays, dates, text, and statistical reductions. They can be used directly on values or inside cube operations such as `apply`, `apply_dimension`, and `reduce_dimension`.

> **NOTE:**
>
> The buttons above filter processes supported by the tracked backends. Availability can differ between backends, so check the connected backend before using a process in a workflow.

## Mathematical operations

### `absolute`

Returns the absolute value of a number.

## Python

``` python
result = openeo.processes.absolute(x=-5)
```

## R

``` r
result <- absolute(x = -5)
```

## JavaScript

``` javascript
const result = builder.absolute({ x: -5 });
```

### `sgn`

Returns the signum of a number: `1` if it is positive, `-1` if it is negative, and `0` if it is zero.

## Python

``` python
result = openeo.processes.sgn(x=-2)
```

## R

``` r
result <- sgn(x = -2)
```

## JavaScript

``` javascript
const result = builder.sgn({ x: -2 });
```

### Trigonometric functions

The `arccos`, `arcosh`, `arcsin`, `arctan`, `arctan2`, `arsinh`, `artanh`, `cos`, `cosh`, `sin`, `sinh`, `tan`, and `tanh` processes calculate trigonometric and inverse trigonometric values. Angles are expressed in radians.

### Rounding

The `ceil`, `floor`, `int`, and `round` processes convert or round numerical values with different rounding rules and precision options.

### Arithmetic

The `add`, `divide`, `mod`, `multiply`, and `subtract` processes perform basic arithmetic on numerical values.

## Python

``` python
result = openeo.processes.add(x=2, y=3)
```

## R

``` r
result <- add(x = 2, y = 3)
```

## JavaScript

``` javascript
const result = builder.add({ x: 2, y: 3 });
```

### Constants and exponentials

The `e` and `pi` processes provide mathematical constants. The `exp`, `ln`, `log`, and `power` processes perform exponential and logarithmic calculations.

### Ranges and roots

The `clip` process limits a value to a range, while `sqrt` calculates its square root.

### Special numerical values

The `is_nan` and `is_infinite` processes test whether a value is NaN or an infinite number.

## Comparisons and logic

### Comparisons

The `between`, `date_between`, `eq`, `neq`, `gt`, `gte`, `lt`, and `lte` processes compare values or test whether values fall within a range.

## Python

``` python
result = openeo.processes.between(x=5, min=0, max=10)
```

## R

``` r
result <- between(x = 5, min = 0, max = 10)
```

## JavaScript

``` javascript
const result = builder.between({ x: 5, min: 0, max: 10 });
```

### Boolean logic

The `and`, `any`, `all`, `not`, `or`, `xor`, and `if` processes combine conditions or select values conditionally.

## Python

``` python
result = openeo.processes.if_(value=True, accept="yes", reject="no")
```

## R

``` r
result <- if_(value = TRUE, accept = "yes", reject = "no")
```

## JavaScript

``` javascript
const result = builder.if({ value: true, accept: "yes", reject: "no" });
```

### Validity checks

The `is_valid` and `is_nodata` processes inspect values and no-data status.

## Arrays and reducers

### Create and modify arrays

The `array_append`, `array_concat`, `array_create`, `array_create_labeled`, and `array_modify` processes create arrays or change their elements and labels.

## Python

``` python
result = openeo.processes.array_append(data=[1, 2], value=3)
```

## R

``` r
result <- array_append(data = c(1, 2), value = 3)
```

## JavaScript

``` javascript
const result = builder.arrayAppend({ data: [1, 2], value: 3 });
```

### Inspect arrays

The `array_contains`, `array_element`, `array_find`, `array_find_label`, and `array_labels` processes find values, labels, indices, or metadata in arrays.

### Transform arrays

The `array_apply`, `array_filter`, and `array_interpolate_linear` processes transform or filter array elements and fill internal gaps by linear interpolation.

### Statistical reducers

The `count`, `extrema`, `first`, `last`, `max`, `mean`, `median`, `min`, `product`, `quantiles`, `sd`, `sum`, and `variance` processes reduce arrays of values to statistical summaries.

## Python

``` python
result = openeo.processes.mean(data=[1, 2, 3])
```

## R

``` r
result <- mean(data = c(1, 2, 3))
```

## JavaScript

``` javascript
const result = builder.mean({ data: [1, 2, 3] });
```

### Ordering and cumulative operations

The `cummax`, `cummin`, `cumproduct`, and `cumsum` processes calculate cumulative results. The `order`, `rearrange`, and `sort` processes order array values or rearrange them using a permutation.

## Dates and text

### Date and time calculations

The `date_difference` process calculates the difference between two temporal values. The `date_shift` process shifts a date or time by a specified amount.

## Python

``` python
result = openeo.processes.date_shift(date="2024-01-01", value=1, unit="month")
```

## R

``` r
result <- date_shift(date = "2024-01-01", value = 1, unit = "month")
```

## JavaScript

``` javascript
const result = builder.dateShift({ date: "2024-01-01", value: 1, unit: "month" });
```

### Text operations

The `text_begins`, `text_concat`, `text_contains`, `text_ends`, and `text_find` processes inspect and combine text values.

## Python

``` python
result = openeo.processes.text_contains(data="openEO documentation", pattern="EO")
```

## R

``` r
result <- text_contains(data = "openEO documentation", pattern = "EO")
```

## JavaScript

``` javascript
const result = builder.textContains({ data: "openEO documentation", pattern: "EO" });
```

### Special constants

The `nan` process creates a NaN value, while `constant` defines a value that can be reused in a process graph.

## Extended and backend-specific operations

The following processes are advertised by one or more tracked backends. They are included here so that the complete backend process inventory is represented in the cube-operations documentation. Their exact parameters and behavior are backend-specific; consult the backend process endpoint before using them.

### Extended numerical operations

The `bit`, `bitwise_and`, `bitwise_not`, `bitwise_or`, and `bitwise_xor` processes perform bit-level operations. The `cast`, `convert_data_type`, `divide_floor`, `max_binary`, `min_binary`, and `scale` processes provide backend-specific type conversion, arithmetic, and scaling operations.

### Population statistics

The `sd_pop` and `variance_pop` processes calculate population standard deviation and population variance.

> **TIP:**
>
> For complete parameter definitions, data types, examples, and errors, consult the [openEO process reference](https://processes.openeo.org/2.0.0-rc.2/).

Back to top
