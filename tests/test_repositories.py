import unittest
from unittest.mock import MagicMock, patch
import sys

from lifeguard.repositories import (
    IMPLEMENTATIONS,
    ValidationRepository,
    declare_implementation,
)

sys.path.append("tests/fixtures")


class TestValidationRepositories(unittest.TestCase):
    def setUp(self):
        if "validation" in IMPLEMENTATIONS:
            IMPLEMENTATIONS.pop("validation")

        self.implementation = MagicMock(name="implementation")
        self.implementation.__name__ = "mocked_implementation"

        with patch("lifeguard.repositories.logger"):
            with patch(
                "lifeguard.repositories.load_implementation"
            ) as mock_load_implementation:
                mock_load_implementation.return_value = self.implementation
                declare_implementation("validation", "TestImplementation")
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
        self.implementation = "fixtures_repositories.TestValidationRepository"

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
            "fixtures_repositories.TestValidationRepository",
            "test",
        )
