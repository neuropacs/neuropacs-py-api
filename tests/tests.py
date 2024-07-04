import unittest
import test_utils
from neuropacs.sdk import Neuropacs

server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/dev"
admin_key = "cdXVNIFzEUbSElTpoVoK4SyRrJ7Zj6n6Y6wgApIc"
reg_key = "7PRHFkrxE71dpBNGw2HaS8PxesOzrZZB2XEWU3Xj"

npcs_admin = Neuropacs(server_url=server_url, api_key=admin_key)
npcs_reg = Neuropacs(server_url=server_url, api_key=reg_key)


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        print("Setting up before a test")
        # Code to set up test environment, if needed

    def tearDown(self):
        print("Cleaning up after a test")
        # Code to clean up test environment, if needed

    def test_successful_connection(self):
        conn = npcs_admin.connect()
        self.assertEqual(test_utils.is_dict(conn), True)

if __name__ == '__main__':
    unittest.main()