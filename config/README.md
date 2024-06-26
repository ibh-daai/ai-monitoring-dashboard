
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

Specifies rules for validating the data to ensure accuracy and consistency.

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

Enables specific tests for regression and classification, each defined by its name and a boolean to enable or disable.

#### Example
```json
{
  "tests": {
    "regression_tests": [
      {
        "name": "mae",
        "description": "Compares with MAE of the reference data. Alerts with a difference of 10%.",
        "enable": true
      }
    ],
    "classification_tests": [
      {
        "name": "accuracy",
        "description": "Compares with accuracy of the reference data. Alerts with a difference of 20%.",
        "enable": true
      }
    ]
  }
}
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