import unittest
from unittest.mock import MagicMock, patch

from lifeguard.actions.database import save_result_into_database


class TestActionDatabase(unittest.TestCase):
    @patch("lifeguard.actions.database.ValidationRepository")
    def test_save_result_into_database(self, mock_validation_repository):
        mock_validation_repository_instance = MagicMock(name="instance")
        mock_validation_repository.return_value = mock_validation_repository_instance

        save_result_into_database("validation_response", {})

        mock_validation_repository_instance.save_validation_result.assert_called_with(
            "validation_response"
        )
