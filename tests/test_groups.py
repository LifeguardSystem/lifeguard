import unittest
from unittest.mock import MagicMock, patch

from lifeguard import NORMAL
from lifeguard.groups import build_group_validations_list, build_groups_summary


class TestGroups(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock(name="repository")

    @patch("lifeguard.groups.VALIDATIONS", {"validation1": {"group": "group1"}})
    @patch("lifeguard.groups.ValidationRepository")
    def test_build_groups_summary(self, mock_validation_repository):
        mock_validation_repository.return_value = self.mock_repository

        validation_response = MagicMock(name="validation_response")
        validation_response.status = NORMAL

        self.mock_repository.fetch_last_validation_result.return_value = (
            validation_response
        )

        response = build_groups_summary()

        self.assertEqual(
            response,
            [
                {
                    "groupName": "group1",
                    "groupID": "group1",
                    "monitorsStateCount": {"normal": 1, "warning": 0, "problem": 0},
                }
            ],
        )

    @patch("lifeguard.groups.VALIDATIONS", {"validation1": {"group": "group1"}})
    @patch("lifeguard.groups.ValidationRepository")
    def test_build_groups_summary_without_validation(self, mock_validation_repository):
        mock_validation_repository.return_value = self.mock_repository

        self.mock_repository.fetch_last_validation_result.return_value = None

        response = build_groups_summary()

        self.assertEqual(
            response,
            [
                {
                    "groupName": "group1",
                    "groupID": "group1",
                    "monitorsStateCount": {"normal": 0, "warning": 0, "problem": 0},
                }
            ],
        )

    @patch(
        "lifeguard.groups.VALIDATIONS",
        {
            "validation1": {"group": "group1", "description": "description1"},
            "validation2": {"group": "group2", "description": "description2"},
        },
    )
    @patch("lifeguard.groups.ValidationRepository")
    def test_build_group_validations_list(self, mock_validation_repository):
        mock_validation_repository.return_value = self.mock_repository

        validation_response = MagicMock(name="validation_response")
        validation_response.status = NORMAL
        validation_response.settings = {"content": {"key": "value"}}

        self.mock_repository.fetch_last_validation_result.return_value = (
            validation_response
        )

        response = build_group_validations_list("group1")

        self.assertEqual(
            response,
            {
                "groupName": "group1",
                "groupID": "group1",
                "monitors": [
                    {
                        "id": "validation1",
                        "name": "validation1",
                        "description": "description1",
                        "status": "normal",
                        "content": {"key": "value"},
                    }
                ],
            },
        )
