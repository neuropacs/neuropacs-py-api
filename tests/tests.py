import unittest
import test_utils
from neuropacs.sdk import Neuropacs

server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/dev"
invalidServerUrl = "https://invalid.execute-api.us-east-2.amazonaws.com/not_real"
admin_key = "cdXVNIFzEUbSElTpoVoK4SyRrJ7Zj6n6Y6wgApIc"
reg_key = "7PRHFkrxE71dpBNGw2HaS8PxesOzrZZB2XEWU3Xj"
origin_type = "Integration Tests"

npcs_admin = Neuropacs(server_url=server_url, api_key=admin_key, origin_type=origin_type)
npcs_reg = Neuropacs(server_url=server_url, api_key=reg_key, origin_type=origin_type)
npcs_invalid = Neuropacs(server_url=server_url, api_key=reg_key, origin_type=origin_type)

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        print("Setting up before a test")
        # Code to set up test environment, if needed

    def tearDown(self):
        print("Cleaning up after a test")
        # Code to clean up test environment, if needed

    # Successful connection
    def test_successful_connection(self):
        conn = npcs_admin.connect()
        timestamp = conn["timestamp"]
        connection_id = conn["connection_id"]
        aes_key = conn["aes_key"]
        self.assertEqual(test_utils.is_dict(conn), True)
        self.assertEqual(test_utils.is_valid_timestamp(timestamp), True)
        self.assertEqual(test_utils.is_valid_uuid4(connection_id), True)
        self.assertEqual(test_utils.is_valid_aes_ctr_key(aes_key), True)

    
if __name__ == '__main__':
    unittest.main()