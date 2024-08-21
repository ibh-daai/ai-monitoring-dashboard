"""
File to store the configuration for the API.
"""

import os


class Config:
    """
    Configuration for the API.
    """

    MONGO_URI = os.getenv("MONGO_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
