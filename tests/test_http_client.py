import unittest
from unittest.mock import patch

from lifeguard.http_client import post


class TestHttpClient(unittest.TestCase):
    @patch("lifeguard.http_client.HTTP_PROXY", "http_proxy")
    @patch("lifeguard.http_client.requests")
    def test_call_post_with_http_proxy(self, mock_requests):
        post("url", data="data", headers="headers")
        mock_requests.post.assert_called_with(
            url="url", headers="headers", data="data", proxies={"http": "http_proxy"}
        )

    @patch("lifeguard.http_client.HTTPS_PROXY", "https_proxy")
    @patch("lifeguard.http_client.requests")
    def test_call_post_with_https_proxy(self, mock_requests):
        post("url", data="data", headers="headers")
        mock_requests.post.assert_called_with(
            url="url", headers="headers", data="data", proxies={"https": "https_proxy"}
        )

    @patch("lifeguard.http_client.requests")
    def test_call_post_without_proxy(self, mock_requests):
        post("url", data="data", headers="headers")
        mock_requests.post.assert_called_with(url="url", headers="headers", data="data")
