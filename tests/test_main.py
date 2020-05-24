from unittest import mock, TestCase

from pyrssaio import main


class TestMain(TestCase):
    @mock.patch('session.request', return_value="TEST")
    def test_fetch_content(self, session):
        main.fetch_content("TEST", session)
