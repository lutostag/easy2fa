from unittest import TestCase
from unittest.mock import patch

import easy2fa


class TestCheckInput(TestCase):
    @patch('builtins.input')
    def test_default(self, mock_input):
        mock_input.return_value = ''
        self.assertEquals(easy2fa.check_input('prompt', default='one'), 'one')
        mock_input.return_value = 'two'
        self.assertEquals(easy2fa.check_input('prompt', default='one'), 'two')

    @patch('builtins.input')
    @patch('builtins.print')
    def test_assertions(self, mock_print, mock_input):
        def assertion(value):
            if value not in ['yes', 'no']:
                return 'use yes or no'

        mock_input.side_effect = ['input', '', 'no']
        self.assertEquals(easy2fa.check_input('prompt', assertion=assertion),
                          'no')
        mock_print.assert_called_with('\tInvalid input: use yes or no')
