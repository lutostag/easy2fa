from unittest import TestCase
from unittest.mock import patch
from argparse import ArgumentParser

import sys
import easy2fa


class TestCmdlineParser(TestCase):
    def __parse(self, *args):
        """Return the output of parsing the given args"""
        sys.argv = list(args)
        sys.argv.insert(0, 'easy2fa')
        return easy2fa.parse_args()

    def test_commands(self):
        for reserved in easy2fa.RESERVED:
            self.assertEqual(self.__parse(reserved), (reserved, None))

    def test_default(self):
        self.assertEqual(self.__parse(), ('generate', None))

    def test_pass_account(self):
        for account in ('one', 'two'):
            for reserved in easy2fa.RESERVED:
                self.assertEqual(self.__parse(reserved, account),
                                 (reserved, account))

    @patch('sys.exit')
    def test_help(self, mock_exit):
        self.__parse('-h')
        mock_exit.assert_called_with(0)

    @patch('sys.exit')
    @patch.object(ArgumentParser, 'print_usage')
    def test_too_many_args(self, mock_usage, mock_exit):
        self.__parse('generate', 'account', 'extra')
        mock_usage.assert_called_with()
        mock_exit.assert_called_with(2)

