import unittest
from unittest.mock import MagicMock, patch

from lifeguard.repositories import ValidationRepository, declare_implementation

IMPLEMENTATION = MagicMock(name="implementation")
declare_implementation("validation", IMPLEMENTATION)


class TestRepositories(unittest.TestCase):
    def setUp(self):
        self.validation_repository = ValidationRepository()

    def test_validation_repository_save_validation_result(self):
        result = MagicMock(name="result")
        self.validation_repository.save_validation_result(result)
        IMPLEMENTATION.save_validation_result.assert_called_with(result)

    def test_validation_repository_fetch_last_validation_result(self):
        validation_name = MagicMock(name="validation_name")
        self.validation_repository.fetch_last_validation_result(validation_name)
        IMPLEMENTATION.fetch_last_validation_result.assert_called_with(validation_name)

    @patch("lifeguard.repositories.logger")
    def test_warning_when_an_implementation_is_overwrited(self, mock_logger):
        declare_implementation("validation", IMPLEMENTATION)
        mock_logger.warning.assert_called_with(
            "overwriting implementation for respository %s", "validation"
        )
