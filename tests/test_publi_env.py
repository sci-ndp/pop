import os
from unittest.mock import patch

from api.config.swagger_settings import Settings


def test_public_variable_default():
    """
    Test that the default value of 'public' is True
    when the 'PUBLIC' environment variable is not set.
    """
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        assert settings.is_public is True


def test_public_variable_true():
    """
    Test that 'public' is True when the 'PUBLIC' environment
    variable is set to 'True'.
    """
    with patch.dict(os.environ, {"PUBLIC": "True"}):
        settings = Settings()
        assert settings.is_public is True


def test_public_variable_false():
    """
    Test that 'public' is False when the 'PUBLIC' environment
    variable is set to 'False'.
    """
    with patch.dict(os.environ, {"PUBLIC": "False"}):
        settings = Settings()
        assert settings.is_public is False
