import unittest
import test_utils
from neuropacs.sdk import Neuropacs

npcs_admin = Neuropacs(server_url=test_utils.server_url, api_key=test_utils.admin_key, origin_type=test_utils.origin_type)
npcs_reg = Neuropacs(server_url=test_utils.server_url, api_key=test_utils.reg_key, origin_type=test_utils.origin_type)
npcs_invalid_key = Neuropacs(server_url=test_utils.server_url, api_key=test_utils.invalid_key, origin_type=test_utils.origin_type)
npcs_invalid_url = Neuropacs(server_url=test_utils.invalidServerUrl, api_key=test_utils.reg_key, origin_type=test_utils.origin_type)

class IntegrationTests(unittest.TestCase):

    # Invalid URL
    # def test_invalid_url(self):
    #     with self.assertRaises(AssertionError) as context:
    #         npcs_invalid_url.connect()
    #     self.assertAlmostEqual(str(context.exception),"Connection creation failed: Public key retrieval failed: HTTPSConnectionPool(host='invalid.execute-api.us-east-2.amazonaws.com', port=443): Max retries exceeded with url: /not_real/api/getPubKey (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x1061c3a60>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known'))")

    # Successful connection
    def test_successful_connection(self):
        conn = npcs_admin.connect()
        self.assertEqual(test_utils.is_valid_session_obj(conn), True)

    # Invalid API key
    def test_invalid_api_key(self):
        with self.assertRaises(Exception) as context:
            npcs_invalid_key.connect()
        self.assertEqual(str(context.exception),"Connection creation failed: API key not found.")

    # Successful order creation
    def test_successful_order_creation(self):
        npcs_admin.connect()
        order_id = npcs_admin.new_job()
        self.assertEqual(test_utils.is_valid_uuid4(order_id), True)

    # Invalid order id
    def test_invalid_order_id(self):
        npcs_reg.connect()
        with self.assertRaises(Exception) as context:
            npcs_reg.run_job(test_utils.product_id, test_utils.invalid_order_id)
        self.assertEqual(str(context.exception),"Job run failed: Bucket not found.")

    # No connection id in request header
    def test_no_connection(self):
        npcs_reg.connection_id = ""
        with self.assertRaises(Exception) as context:
            npcs_reg.new_job()
        self.assertEqual(str(context.exception),"Job creation failed: No connection ID in request header.")

    # Successful status check
    def test_successful_status_check(self):
        npcs_admin.connect()
        order_id = npcs_admin.check_status(order_id="TEST")
        self.assertEqual(test_utils.is_valid_status_obj(order_id), True)


    # Invalid order id in status check
    def test_invalid_order_id_in_status_check(self):
        npcs_admin.connect()
        with self.assertRaises(Exception) as context:
            order_id = npcs_admin.check_status(order_id="Not_Valid")
        self.assertEqual(str(context.exception),"Status check failed: Bucket not found.")
        
    # # Successful dataset upload
    # def test_successful_dataset_upload(self):
    #     npcs_admin.connect()
    #     order_id = npcs_admin.new_job()
    #     upload_status = npcs_admin.upload_dataset("./tests/test_dataset", order_id=order_id, dataset_id=order_id)
    #     dataset_id = upload_status["dataset_id"]
    #     state = upload_status["state"]
    #     self.assertEqual(test_utils.is_dict(upload_status), True)
    #     self.assertEqual(state, "success")
    #     self.assertEqual(dataset_id, order_id)

    
if __name__ == '__main__':
    unittest.main()