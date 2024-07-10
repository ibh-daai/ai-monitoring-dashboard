
# AI Model Monitoring System Configuration Guide

## Introduction

This documentation is designed to assist users in configuring the AI Model Monitoring system developed by the AIDE Lab. The configuration should be specified in the provided `config.json` file.

## Configuration Sections

The configuration file is structured into several key sections: `model_config`, `columns`, `validation_rules`, `tests`, and `alerts`. Each section plays a crucial role in setting up the monitoring system accurately.

### Model Configuration (`model_config`)

This section defines the basic settings of the model.

- **model_id** (`string`): Unique identifier for the model.

- **model_type** (`object`):

  - **regression** (`boolean`): Enable if the model includes regression metrics.

  - **binary_classification** (`boolean`): Enable if the model includes binary classification metrics.

- **provide_reference** (`boolean`): Should be set to `false` if the system is expected to automatically split the initial dataset for reference purposes.

#### Example

```json
{
  "model_config": {
    "model_id": "bone_age_01",
    "model_type": {
      "regression": true,
      "binary_classification": true
    },
    "provide_reference": false
  }
}
```
### Columns

Defines the mapping of data columns to required schema properties.

-   **study_id** (`string`): Identifier for the study.
-   **model_id** (`string`): Identifier for the model.
-   **sex** (`string`): Patient's sex.
-   **hospital** (`string`): Hospital where the data was collected.
-   **age** (`string`): Patient's age.
-   **instrument_type** (`string`): Type of instrument used to make the prediction.
-   **predictions** (`object`):
    -   **regression_prediction** (`string`): Column for predicted regression values.
    -   **classification_prediction** (`string`): Column for predicted classification values.
-   **labels** (`object`):
    -   **regression_label** (`string`): Column for regression labels.
    -   **classification_label** (`string`): Column for classification labels.
-   **features** (`array` of `string`): Names of features used in the model.
-   **timestamp** (`string`, nullable): Column for timestamp data, if applicable.

#### Example
```json
{
  "columns": {
    "study_id": "StudyID",
    "model_id": "ModelID",
    "sex": "sex",
    "hospital": "hospital",
    "age": "chronological_age",
    "instrument_type": "machine_type",
    "predictions": {
      "regression_prediction": "predicted_age",
      "classification_prediction": "classification"
    },
    "labels": {
      "regression_label": "label",
      "classification_label": "classification_label"
    },
    "features": [
      "standard_deviation",
      "two_standard_deviations",
      "upper_limit",
      "lower_limit",
      "closest_age"
    ],
    "timestamp": null
  }
}
```
### Validation Rules (`validation_rules`)

Specifies rules for validating the data to ensure accuracy and consistency. The enum vs range is used to split columns into categorical and numerical columns. The validation rules are used to ensure that the data is within the expected range or values, as defined in the configuration. Will not throw an error if the data is outside the range, but will be flagged as an alert.

-   Enum and Range are used to define acceptable parameters for each feature.
-   **type** (`string`): 'enum' for a set of acceptable strings, 'range' for numerical boundaries.

#### Example
```json
{
  "validation_rules": {
    "sex": {
      "type": "enum",
      "values": ["M", "F"]
    },
    "hospital": {
      "type": "enum",
      "values": ["Credit Valley Hospital", "Mississauga Hospital", "Queensway Hospital"]
    },
    "age": {
      "type": "range",
      "min": 0,
      "max": 400
    }
  }
}
```
### Tests

Enables specific tests for regression and classification. To add tests, include the name of the test in its corresponding category, as seen below and in the example to follow. For more information on any test, please check [Evidently AI](https://docs.evidentlyai.com/reference/all-tests). ***Note:*** *When doing a column specific test, use the exact name of the column in your Dataframe, NOT the generic config name* The tests to choose from are:
#### Data Quality Tests
-   **num_rows**: Checks the number of rows in the dataset against the reference data.
-   **num_cols**: Checks the number of columns in the dataset against the reference data.
-   **num_empty_rows**: Checks the number of empty rows in the dataset against the reference data.
-   **num_empty_cols**: Checks the number of empty columns in the dataset against the reference data.
-   **num_duplicated_rows**: Checks the number of duplicated rows in the dataset against the reference data.
-   **num_duplicated_cos**: Checks the number of duplicated columns in the dataset against the reference data.
-   **col_types**: Checks the column types in the dataset against the reference data.
-   **col_regex**: Tests the number of values in a column that do not match a defined regular expression, against reference data.
parameters:
    -  **column_name**: Name of the column to be tested.
    -  **regex**: Regular expression to be tested against.
-   **num_missing_values**: Checks the number of missing values in the dataset against the reference data.
parameters:
    -  **missing_values**: (optional) List of missing values to be checked against.
-   **share_missing_values**: Checks the share of missing values in the dataset against the reference data.
parameters:
    -  **missing_values**: (optional) List of missing values to be checked against.
-   **num_cols_with_missing_values**: Checks the number of columns with missing values in the dataset against the reference data.
parameters:
    -  **missing_values**: (optional) List of missing values to be checked against.
-   **num_rows_with_missing_values**: Checks the number of rows with missing values in the dataset against the reference data.
parameters:
    -  **missing_values**: (optional) List of missing values to be checked against.
-   **test_col_range**: Checks the range of values in a numerical column. ***Use this test to ensure that the values within a numerical column are within a defined range***
parameters:
    -  **column_name**: Name of the column to be tested.
    -  **left**: Minimum value for the column.
    -  **right**: Maximum value for the column.
-   **test_col_list**: Checks the values in a categorical column against a set of acceptable values. ***Use this test to ensure that the values within a categorical column are within a defined set of values***
parameters:
    -  **column_name**: Name of the column to be tested.
    -  **values**: (optional) List of acceptable values for the column.

#### Data Drift Tests
-   **num_drifted_cols**: Checks the number of columns that have drifted from the reference data.
parameters:
    -  **columns**: (optional) List of columns to be checked for drift.
    -  Check documentation for more parameters.
-   **share_drifted_cols**: Checks the share of columns that have drifted from the reference data.
parameters:
    -  **columns**: (optional) List of columns to be checked for drift.
    -  Check documentation for more parameters.
-   **test_drift**: Checks the drift of a column from the reference data.
parameters:
    -  **column_name**: Name of the column to be tested.
    -  Check documentation for more parameters.

#### Regression Tests
-   **mae**: Computes the Mean Absolute Error (MAE) and compares it to the reference
-   **rmse**: Computes the Root Mean Squared Error (RMSE) and compares it to the reference
-   **me**: Computes the Mean Error (ME) and compares it to the reference
-   **mape**: Computes the Mean Absolute Percentage Error (MAPE) and compares it to the reference
-   **abs_max_error**: Computes the Absolute Maximum Error and compares it to the reference
-   **r2**: Computes the R2 score and compares it to the reference

#### Classification Tests
-   **accuracy**: Computes the accuracy and compares it to the reference
-   **precision**: Computes the precision/ppv and compares it to the reference
-   **recall**: Computes the recall/sensitivity/tpr and compares it to the reference
-   **f1**: Computes the F1 score and compares it to the reference
-   **precision_by_class**: Computes the precision by class and compares it to the reference
parameters:
    -  **label**: Name of the class to be tested.
-   **recall_by_class**: Computes the recall by class and compares it to the reference
parameters:
    -  **label**: Name of the class to be tested.
-   **f1_by_class**: Computes the F1 score by class and compares it to the reference
parameters:
    -  **label**: Name of the class to be tested.
-   **tpr**: Computes the True Positive Rate (TPR) and compares it to the reference
-   **tnr**: Computes the True Negative Rate (TNR)/specificity and compares it to the reference
-   **fpr**: Computes the False Positive Rate (FPR)/type 1 error and compares it to the reference
-   **fnr**: Computes the False Negative Rate (FNR)/type 2 error and compares it to the reference

To add a test, include the name of the test in its corresponding category, and add any optional and/or required parameters to a `params` object. The `params` is optional and should only be included if the test requires additional parameters. Within the `params` object, include the required parameters for the test with the key being the parameter name and the value being the parameter value.
#### Example
```json
"tests": {
    "data_quality_tests": [
      {
        "name": "num_cols"
      },
      {
        "name": "num_empty_rows"
      },
      {
        "name": "num_duplicated_rows"
      },
      {
        "name": "num_duplicated_cols"
      },
      {
        "name": "col_types"
      },
      {
        "name": "num_missing_values"
      },
      {
        "name": "test_col_range",
        "params": {
          "column_name": "closest_age",
          "left": 0,
          "right": 216
        }
      },
      {
        "name": "test_col_list",
        "params": {
          "column_name": "hospital",
          "values": [
            "Credit Valley Hospital",
            "Mississauga Hospital",
            "Queensway Hospital"
          ]
        }
      }
    ],
    "data_drift_tests": [
      {
        "name": "num_drifted_cols"
      },
      {
        "name": "share_drifted_cols"
      }
    ],
    "regression_tests": [
      {
        "name": "mae"
      }
    ],
    "classification_tests": [
      {
        "name": "accuracy"
      },
      {
        "name": "precision"
      },
      {
        "name": "recall"
      },
      {
        "name": "f1"
      },
      {
        "name": "tnr"
      },
      {
        "name": "fpr"
      },
      {
        "name": "fnr"
      }
    ]
  },
```
### Alerts (`alerts`)

Configures alert settings for the monitoring system.

-   **enable** (`boolean`): Enable or disable alerts.
-   **alert_links** (`array` of `objects`): Configure alert methods and destinations, such as Microsoft Teams.

#### Example
```json
"alerts": {
    "enable": true,
    "alert_links": [
        {
            "type": "microsoft teams channel",
            "url": "<TODO>"
        }
    ]
}
````