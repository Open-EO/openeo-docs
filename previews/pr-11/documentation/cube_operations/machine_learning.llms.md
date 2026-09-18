# Machine Learning Support

The openEO API provides certain machine-learning capabilities that allow users to extract features from data cubes and perform model training and prediction. While there is limited support for training a model directly within the API, it facilitates easier data extraction and preparation for machine-learning workflows. Additionally, for the inference workflow, openEO provides methods to use the trained or loaded models for prediction.

Please note that this support can be backend-specific and may vary depending on the openEO backend you are connected to.

> **NOTE:**
>
> The buttons above let you filter processes supported by different backends. Selecting or deselecting a backend will show or hide the relevant sections in the documentation. However, please note that it is based on the latest documentation rendering. Thus, please refer to the [openEO Hub](https://hub.openeo.org/) for the most up-to-date information.

## A typical ML workflow

  Generally, a machine-learning workflow can be broken down into the following steps:

1.  Extract and prepare relevant features from the model training.
2.  Train and validate a machine-learning model using the prepared features.
3.  Apply the trained model to make predictions on new data.

In the above workflow, openEO support can be found primarily in:

1.  Feature preparation and extraction: Supports preparing and extracting relevant features from data cubes, such as selecting bands, computing indices, and aggregating temporally. These features can also be downloaded to feed into the training of machine-learning models.
2.  Model Training: Limited support for training machine-learning models directly within the backend. Users may need to download prepared features and train models externally before using them for prediction within openEO. Nevertheless, widely used models such as random forests are defined in openEO as standard processes, allowing for consistent usage across different backends.
3.  Model Prediction: Once a model is trained, openEO provides processes to apply the model to new data cubes for prediction. The exact process and required input format may vary depending on the backend.

On this page, we provide an overview of the machine-learning support in openEO, including feature preparation, model training, and prediction.

## Feature preparation

Features can be anything derived from the original data cubes that are relevant for the machine-learning task at hand. This includes selecting specific bands, computing indices, aggregating over time, or any other transformation that helps prepare the data for model training and prediction. Moreover, the selection and preparation of features widely depend on the specific machine-learning task.

For example, if the task is to classify Land Cover types, relevant features might include spectral bands, vegetation indices, and temporal aggregates that capture seasonal variations. These features can then be used to train a classifier to distinguish between different land cover classes.

The prepared features can be saved as a single raster of a specified size or as a tabular dataset suitable for machine-learning model training.

## Random Forest Classifier in openEO

### Train a random forest classifier

The `fit_class_random_forest` process trains a random forest classifier on labelled training features. It requires specifying the target column containing the class labels, as well as optionally other model parameters. The backend determines the supported feature layout, label column, and model parameters.

## Python

``` python

feature_collection = {"type": "FeatureCollection", "features": [
    {
        "type": "Feature",
        "properties": {"id": "b3dw-wd23", "target": 3},
        "geometry": {"type": "Point", "coordinates": [3.4, 51.1]}
    },
    {
        "type": "Feature",
        "properties": {"id": "r8dh-3jkd", "target": 5},
        "geometry": {"type": "Point", "coordinates": [3.6, 51.2]}
    }
]}
model = aggregated_vectorcube.fit_class_random_forest(target=feature_collection)
```

## R

``` r
model <- aggregated_vectorcube$fit_class_random_forest(target=feature_collection)
```

## JavaScript

``` javascript
const model = aggregated_vectorcube.fit_class_random_forest({target: feature_collection});
```

### Train a random-forest regressor

The `fit_regr_random_forest` process trains a random-forest regressor on labelled training data with a continuous target. The difference between the classification and regression processes lies in the type of target variable: classification uses discrete class labels, while regression uses continuous values.

## Python

``` python
feature_collection = {"type": "FeatureCollection", "features": [
    {
        "type": "Feature",
        "properties": {"id": "b3dw-wd23", "value": 3.5},
        "geometry": {"type": "Point", "coordinates": [3.4, 51.1]}
    },
    {
        "type": "Feature",
        "properties": {"id": "r8dh-3jkd", "value": 5.2},
        "geometry": {"type": "Point", "coordinates": [3.6, 51.2]}
    }
]}
cube = connection.load_collection(
    "SENTINEL2",
    temporal_extent=[start, end],
    spatial_extent=bbox,
    bands=["B02", "B03", "B04"]
)
aggregated_vectorcube = cube.reduce_dimension(dimension="t", reducer="mean")

model = aggregated_vectorcube.fit_regr_random_forest(target=feature_collection)
```

## R

``` r
model <- aggregated_vectorcube$fit_regr_random_forest(target=feature_collection)
```

## JavaScript

``` javascript
const model = aggregated_vectorcube.fit_regr_random_forest({target: feature_collection});
```

### Predict with a random forest

Once a random-forest model has been trained using `fit_class_random_forest` or `fit_regr_random_forest`, it can be used to make predictions on new feature cubes. Use `predict_random_forest` for this purpose. It returns predictions based on the trained model.

Once a random-forest model has been trained using `fit_class_random_forest` or `fit_regr_random_forest`, it can be used to make predictions on new feature cubes. Use `predict_random_forest` for this purpose. It returns predictions based on the trained model.

## Python

``` python
prediction = features.predict_random_forest(model=model, dimension="bands")
```

## R

``` r
prediction <- features$predict_random_forest(model=model, dimension="bands")
```

## JavaScript

``` javascript
const prediction = features.predict_random_forest({model: model, dimension: "bands"});
```

### Load a machine-learning model

During the prediction phase, if a machine-learning model has been previously trained and saved, it can be loaded using `load_ml_model` to avoid retraining and ensure consistent predictions. Users can use the `load_ml_model` function to retrieve the model before making predictions. Alternatively, this model can be saved to external storage for later reuse or sharing across different workflows.

## Python

``` python
model = connection.load_ml_model(model_id="my-model")
```

## R

``` r
model <- connection$load_ml_model(model_id="my-model")
```

## JavaScript

``` javascript
const model = connection.load_ml_model({model_id: "my-model"});
```

> **TIP:**
>
> - [Forest Fire Mapping using Random Forest](../../client_examples/openeo-community-examples/python/RandomForest-ForestFire/RandomForestModelTraining.ipynb)
> - [Reusing openEO Workflows Saved as UDPs](../../client_examples/openeo-community-examples/python/RandomForest-ForestFire/RandomForestModelInference_AsUDP.ipynb)
> - [Running ML Inference with an ONNX Model](../../client_examples/openeo-community-examples/python/OnnxMLInference/Onnx_ML_Inference.ipynb)
> - [Dimensionality Reduction using Sentinel-2 (PCA)](../../client_examples/openeo-community-examples/python/DimensionalityReduction/Dimensionality%20Reduction.ipynb)
> - [ML-Ready Data Preparation using openEO](../../client_examples/openeo-community-examples/python/ExtractingTrainingData/ML_ready_data_extraction.ipynb)
> - [TESSERA Pixel Embeddings from Sentinel-1/2](../../client_examples/openeo-community-examples/python/TesseraEmbedding/TesseraEmbedding.ipynb)
>
> More notebooks are listed on the [sample notebooks page](../../examples.llms.md).

### Save a machine-learning model

Using the `save_ml_model` function, users can save a machine-learning model as part of a batch job to persist a trained model for later prediction or sharing.

## Python

``` python
saved = model.save_ml_model(model_id="my-model")
```

## R

``` r
saved <- model$save_ml_model(model_id="my-model")
```

## JavaScript

``` javascript
const saved = model.save_ml_model({model_id: "my-model"});
```

### Predict with a random forest model

Use `predict_random_forest` when the backend supports random forest models. Exact model formats, input schema, and output labels must be checked in backend metadata.

## Python

``` python
prediction = features.predict_random_forest(model=model)
```

## R

``` r
prediction <- features$predict_random_forest(model=model)
```

## JavaScript

``` javascript
const prediction = features.predict_random_forest({model: model});
```

### Predict with an ONNX model

Use `predict_onnx` to apply a portable ONNX model when the backend advertises ONNX inference. The model input order and tensor shape must match the feature cube.

## Python

``` python
prediction = features.predict_onnx(model=model)
```

## R

``` r
prediction <- features$predict_onnx(model=model)
```

## JavaScript

``` javascript
const prediction = features.predict_onnx({model: model});
```

## Reuse a machine-learning model

While openEO supports training a Random Forest model, users often prefer to use a deep learning model trained externally, which can then be reused for predictions within the openEO framework.

### Load as a package

These models can be saved as ONNX files and passed in as dependency packages within a UDF.

A similar example is: [ONNX ML Inference](https://github.com/Open-EO/openeo-community-examples/tree/main/python/OnnxMLInference)

### Save as a UDP

Users can save the externally trained model within a User-Defined Process (UDP) to make it reusable within the openEO workflow. This allows the model to be easily shared and applied to different datasets without retraining. For more information on creating and using UDPs, visit the [User-Defined Processes](../../documentation/cube_operations/udp.llms.md) page.

Back to top
