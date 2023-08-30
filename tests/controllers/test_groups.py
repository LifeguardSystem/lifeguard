import unittest
from unittest.mock import patch

from lifeguard.controllers.groups import groups_summary_controller, groups_controller


class TestGroupsControllers(unittest.TestCase):
    @patch("lifeguard.controllers.groups.build_groups_summary")
    def test_groups_summary_controller(self, mock_build_groups_summary):
        mock_build_groups_summary.return_value = ""

        response = groups_summary_controller()

        self.assertEqual(response, "")
        mock_build_groups_summary.assert_called_with()

    @patch("lifeguard.controllers.groups.build_groups_summary")
    @patch("lifeguard.controllers.groups.send_status")
    def test_groups_summary_controller_with_exception(
        self, mock_send_status, mock_build_groups_summary
    ):
        mock_build_groups_summary.side_effect = Exception("exception")

        response = groups_summary_controller()

        self.assertEqual(response, mock_send_status.return_value)
        mock_build_groups_summary.assert_called_with()
        mock_send_status.assert_called_with(500, content_type="application/json")

    @patch("lifeguard.controllers.groups.build_group_validations_list")
    def test_groups_controller(self, mock_build_group_validations_list):
        mock_build_group_validations_list.return_value = ""

        response = groups_controller("group")

        self.assertEqual(response, "")
        mock_build_group_validations_list.assert_called_with("group")

    @patch("lifeguard.controllers.groups.build_group_validations_list")
    @patch("lifeguard.controllers.groups.send_status")
    def test_groups_controller_with_exception(
        self, mock_send_status, mock_build_group_validations_list
    ):
        mock_build_group_validations_list.side_effect = Exception("exception")

        response = groups_controller("group")

        self.assertEqual(response, mock_send_status.return_value)
        mock_build_group_validations_list.assert_called_with("group")
        mock_send_status.assert_called_with(500, content_type="application/json")
