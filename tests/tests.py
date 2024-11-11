import unittest
import test_utils
import neuropacs
# import sdk

npcs_admin = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.admin_key, origin_type=test_utils.origin_type)
npcs_reg = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.reg_key, origin_type=test_utils.origin_type)
npcs_invalid_key = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.invalid_key, origin_type=test_utils.origin_type)
npcs_no_usages = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.no_usages_remaining_api_key, origin_type=test_utils.origin_type)
npcs_invalid_url = neuropacs.init(server_url=test_utils.invalidServerUrl, api_key=test_utils.reg_key, origin_type=test_utils.origin_type)

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
        self.assertEqual(str(context.exception),"Connection failed: API key not found.")

    # Successful order creation
    def test_successful_order_creation(self):
        npcs_admin.connect()
        order_id = npcs_admin.new_job()
        self.assertEqual(test_utils.is_valid_uuid4(order_id), True)


    # Missing connnection parameters
    def test_missing_connection_parameters(self):
        with self.assertRaises(Exception) as context:
            npcs_admin.connection_id = None
            npcs_admin.aes_key = None
            npcs_admin.new_job()
        self.assertEqual(str(context.exception),"Job creation failed: Missing session parameters, start a new session with 'connect()' and try again.")

    # Successful dataset upload
    def test_successful_dataset_upload(self):
        npcs_admin.connect()
        order_id = npcs_admin.new_job()
        upload_status = npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_git)
        self.assertEqual(upload_status, True)

    # Successful job run
    def test_successful_job_run(self):
        npcs_admin.connect()
        order_id = npcs_admin.new_job()
        upload_status = npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_git_single)
        job = npcs_admin.run_job(order_id=order_id, product_name=test_utils.product_id)
        self.assertEqual(upload_status, True)
        self.assertEqual(job, 202)

    # Invalid order id
    def test_invalid_order_id(self):
        npcs_reg.connect()
        with self.assertRaises(Exception) as context:
            npcs_reg.run_job(test_utils.invalid_order_id, test_utils.product_id)
        self.assertEqual(str(context.exception),"Job run failed: Bucket not found.")

    # No API key usages remaining
    def test_no_api_key_usages_remaining(self):
        with self.assertRaises(Exception) as context:
            npcs_no_usages.connect()
            order_id = npcs_no_usages.new_job()
            npcs_no_usages.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_git_single)
            npcs_no_usages.run_job(order_id=order_id, product_name=test_utils.product_id)
        self.assertEqual(str(context.exception),"Job run failed: No API key usages remaining.")

    # No invalid product ID
    def test_invalid_product(self):
        with self.assertRaises(Exception) as context:
            npcs_admin.connect()
            order_id = npcs_admin.new_job()
            npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_git_single)
            npcs_admin.run_job(order_id=order_id, product_name=test_utils.invalid_product_id)
        self.assertEqual(str(context.exception),"Job run failed: Product not found.")

    # Successful status check
    def test_successful_status_check(self):
        npcs_admin.connect()
        status = npcs_admin.check_status(order_id="TEST")
        self.assertEqual(test_utils.is_valid_status_obj(status), True)

    # Invalid order id in status check
    def test_invalid_order_id_in_status_check(self):
        npcs_admin.connect()
        with self.assertRaises(Exception) as context:
            status = npcs_admin.check_status(order_id="Not_Valid")
        self.assertEqual(str(context.exception),"Status check failed: Bucket not found.")

    # Successful result retrieval in txt format
    def test_successful_result_retrieval_txt(self):
        npcs_admin.connect()
        results = npcs_admin.get_results(order_id="TEST", format="txt")
        self.assertEqual(test_utils.is_valid_result_txt(results), True)

    # Successful result retrievel in json format
    def test_successful_result_retrieval_json(self):
        npcs_admin.connect()
        results = npcs_admin.get_results(order_id="TEST", format="JSON")
        self.assertEqual(test_utils.is_valid_result_json(results), True)

    # Invalid result format
    def test_invalid_format_in_result_retrieval(self):
        npcs_admin.connect()
        with self.assertRaises(Exception) as context:
            results = npcs_admin.get_results(order_id="TEST", format="INVALID")
        self.assertEqual(str(context.exception), "Result retrieval failed: Invalid format.")
        


    
if __name__ == '__main__':
    unittest.main()