AI Model Monitoring System Configuration Guide
==============================================

Introduction
------------

This documentation is written to help you understand and configure the AI Model Monitoring system developed by the AIDE Lab using the provided `config.yaml` file. It is important to note that both the reference data and current data must be in the exact same format outlined below.

Sections
--------

The configuration file is structured into four sections: `model_config`, `data_handling`, `tests`, and `alerts`. Examples are shown in color.

### model_config

-   **model_id** (`string`): Unique identifier for the model.
-   **model_type** (`object`): Set either `binary_classification` and/or `regression` to `true`. This decides which metrics will be shown.

#### Example
```yaml
model_config:
  model_id: "bone_age_01"
  model_type:
    regression: true
    binary_classification: true
```
### data_handling

Defines how to map your data columns to the required schema properties. If a required column is missing, replace the column name with `null`.

-   **columns** (`object`):
    -   **study_id** (`string`): Unique identifiers for the study.
    -   **patient_id** (`string`): Unique identifiers for the patients.
    -   **model_id** (`string`): Unique identifier for the model.
    -   **predictions** (`object`):
        -   **regression** (`string`): Column name for predicted regression values.
        -   **classification** (`string`): Column name for predicted classification values.
    -   **labels** (`object`):
        -   **regression** (`string`): Column name for regression labels.
        -   **classification** (`string`): Column name for classification labels.
    -   **features** (`array` of `string`): Column names for all the features. Optional, can include as many features as you like.
    -   **timestamp** (`string`): Column name for timestamps.

#### Example
```yaml
data_handling:
  columns:
    study_id: "StudyInstanceUID"
    patient_id: "PatientID"
    model_id: "modelID"
    predictions:
      regression: "predicted_age"
      classification: "classification"
    labels:
      regression: "label"
      classification: "classification_label"
    features:
      - "sex"
      - "chronological_age"
      - "standard_deviation"
      - "two_standard_deviation"
      - "upper_limit"
      - "lower_limit"
      - "closest_age"
    timestamp: "timestamp"
```
### tests

Enable or disable specific tests for regression and classification models.

-   **regression_tests** (`array` of `objects`):
    -   **name** (`string`): The name of the test (do not edit).
    -   **description** (`string`): A brief description of the test (optional edit).
    -   **enable** (`boolean`): Set to `true` to enable the test and `false` to disable.
-   **classification_tests** (`array` of `objects`):
    -   **name** (`string`): The name of the test (do not edit).
    -   **description** (`string`): A brief description of the test (optional edit).
    -   **enable** (`boolean`): Set to `true` to enable the test and `false` to disable.

#### Example
```yaml
tests:
  regression_tests:
    - name: "mae"
      description: ""
      enable: true
    - name: "rmse"
      description: ""
      enable: true
    - name: "mean_error"
      description: ""
      enable: false
    - name: "mape"
      description: ""
      enable: false
    - name: "absolute_max_error"
      description: ""
      enable: false
    - name: "r2"
      description: ""
      enable: false

  classification_tests:
    - name: "accuracy"
      description: ""
      enable: true
    - name: "precision"
      description: ""
      enable: true
    - name: "recall"
      description: ""
      enable: true
    - name: "f1"
      description: ""
      enable: true
    - name: "specificity"
      description: ""
      enable: true
    - name: "fpr"
      description: ""
      enable: false
    - name: "fnr"
      description: ""
      enable: false
    - name: "roc_auc"
      description: ""
      enable: false
```

### alerts

Configure alert settings for the system.

-   **enable** (`boolean`): Set to `true` to enable alerts, `false` to disable.
-   **alert_links** (`array` of `object`):
    -   **type** (`string`): The type of alert method (supports only Microsoft Teams channel currently).
    -   **url** (`string`): URL for the Teams channel (or other alert type).

#### Example
```yaml
alerts:
  enable: true
  alert_links:
    - type: "microsoft teams channel"
      url: "https://example.com/webhook_url"
````