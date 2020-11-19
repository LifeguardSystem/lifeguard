import unittest
from unittest.mock import MagicMock, patch

from lifeguard.repositories import (
    ValidationRepository,
    declare_implementation,
    IMPLEMENTATIONS,
)


class TestValidationRepositories(unittest.TestCase):
    def setUp(self):
        if "validation" in IMPLEMENTATIONS:
            IMPLEMENTATIONS.pop("validation")

        self.implementation = MagicMock(name="implementation")
        self.implementation.__name__ = "mocked_implementation"

        with patch("lifeguard.repositories.logger"):
            declare_implementation("validation", self.implementation)
        self.validation_repository = ValidationRepository()

    def test_validation_repository_save_validation_result(self):
        result = MagicMock(name="result")
        self.validation_repository.save_validation_result(result)
        self.implementation.save_validation_result.assert_called_with(result)

    def test_validation_repository_fetch_last_validation_result(self):
        validation_name = MagicMock(name="validation_name")
        self.validation_repository.fetch_last_validation_result(validation_name)
        self.implementation.fetch_last_validation_result.assert_called_with(
            validation_name
        )


class TestRepositoriesFunctions(unittest.TestCase):
    def setUp(self):
        if "test" in IMPLEMENTATIONS:
            IMPLEMENTATIONS.pop("test")

        self.implementation = MagicMock(name="implementation")
        self.implementation.__name__ = "mocked_implementation"

    @patch("lifeguard.repositories.logger")
    def test_warning_when_an_implementation_is_overwrited(self, mock_logger):
        declare_implementation("test", self.implementation)
        declare_implementation("test", self.implementation)
        mock_logger.warning.assert_called_with(
            "overwriting implementation for respository %s", "test"
        )

    @patch("lifeguard.repositories.logger")
    def test_info_when_an_implementation_is_declared(self, mock_logger):
        declare_implementation("test", self.implementation)
        mock_logger.info.assert_called_with(
            "loading implementation %s for repository %s",
            "mocked_implementation",
            "test",
        )
