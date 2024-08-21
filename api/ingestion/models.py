"""
Models for MongoDB collections.
"""

from datetime import datetime, timezone


class Result:
    """
    The Result model.
    """

    def __init__(
        self,
        study_id,
        sex,
        hospital,
        age,
        regression_prediction,
        classification_prediction,
        features,
        timestamp,
        instrument_type=None,
        patient_class=None,
    ):
        self.study_id = study_id
        self.sex = sex
        self.hospital = hospital
        self.age = age
        self.instrument_type = instrument_type
        self.patient_class = patient_class
        self.regression_prediction = regression_prediction
        self.classification_prediction = classification_prediction
        self.features = features
        self.timestamp = timestamp or datetime.now(timezone.utc)


class Label:
    """
    The Label model.
    """

    def __init__(self, study_id, timestamp, regression_label=None, classification_label=None):
        self.study_id = study_id
        self.regression_label = regression_label
        self.classification_label = classification_label
        self.timestamp = timestamp or datetime.now(timezone.utc)
