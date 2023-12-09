import unittest
from unittest.mock import patch, Mock
from neuropacs.sdk import Neuropacs

# RUN TESTS: python -m unittest tests.tests_neuropacs

class UnitTests(unittest.TestCase):

    def setUp(self):
        self.npcs = Neuropacs("m0ig54amrl87awtwlizcuji2bxacjm", "http://localhost:5000")

    # Test 1: generate_aes_key() - Expected Result
    @patch('neuropacs.sdk.Neuropacs.generate_aes_key')
    def test_generate_aes_key_1(self, mock_generate_aes_key):
        mock_generate_aes_key.return_value = "1234567890123456"

        result = self.npcs.generate_aes_key()

        self.assertEqual(result, "1234567890123456")

        mock_generate_aes_key.assert_called_once()

    


