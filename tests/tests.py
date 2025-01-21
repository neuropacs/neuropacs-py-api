import unittest
import test_utils
import neuropacs
import datetime

npcs_admin = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.admin_key, origin_type=test_utils.origin_type)
npcs_reg = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.reg_key, origin_type=test_utils.origin_type)
npcs_invalid_key = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.invalid_key, origin_type=test_utils.origin_type)
npcs_no_usages = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.no_usages_remaining_api_key, origin_type=test_utils.origin_type)
npcs_invalid_url = neuropacs.init(server_url=test_utils.invalidServerUrl, api_key=test_utils.reg_key, origin_type=test_utils.origin_type)

class IntegrationTests(unittest.TestCase):

    '''
    Tests todo:
    - invalid url
    - admin key access to non admin job info (should succeed)
    - non admin key access to admin job info (should fail)
    '''
    
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
        upload_status = npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_local)
        self.assertEqual(upload_status, True)

    # Invalid dataset path
    def test_invalid_dataset_path(self):
        npcs_admin.connect()
        order_id = npcs_admin.new_job()
        with self.assertRaises(Exception) as context:
            npcs_admin.upload_dataset_from_path(order_id=order_id, path="/not/real")
        self.assertEqual(str(context.exception),"Error uploading dataset from path: Path not a directory.")

    # Invalid order ID
    def test_invalid_order_id_upload(self):
        npcs_admin.connect()
        with self.assertRaises(Exception) as context:
            npcs_admin.upload_dataset_from_path(order_id="no_real", path=test_utils.dataset_path_local)
        self.assertEqual(str(context.exception),"Error uploading dataset from path: Multipart upload initialization failed: Bucket not found.")

    # Successful job run
    def test_successful_job_run(self):
        npcs_admin.connect()
        order_id = npcs_admin.new_job()
        upload_status = npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_local_single)
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
            npcs_no_usages.run_job(order_id=order_id, product_name=test_utils.product_id)
        self.assertEqual(str(context.exception),"Job run failed: No API key usages remaining.")

    # Invalid product ID
    def test_invalid_product(self):
        with self.assertRaises(Exception) as context:
            npcs_admin.connect()
            order_id = npcs_admin.new_job()
            npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_local_single)
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

    # Successful report retrieval in txt format
    def test_successful_report_retrieval_txt(self):
        import sdk
        npcs_test = sdk.Neuropacs(server_url="https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox", api_key="generate_api_key", origin_type=test_utils.origin_type)
        npcs_test.connect()

        today = datetime.date.today()
        ten_days_ago = today - datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_ago_str = f"{ten_days_ago.month}/{ten_days_ago.day}/{ten_days_ago.year}"
      
        results = npcs_test.get_report(format="txt", start_date=ten_days_ago_str, end_date=today_str)
        self.assertEqual(test_utils.is_valid_report_txt(results), True)

    # Successful report retrieval in json format
    def test_successful_report_retrieval_json(self):
        import sdk
        npcs_test = sdk.Neuropacs(server_url="https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox", api_key="generate_api_key", origin_type=test_utils.origin_type)
        npcs_test.connect()

        today = datetime.date.today()
        ten_days_ago = today - datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_ago_str = f"{ten_days_ago.month}/{ten_days_ago.day}/{ten_days_ago.year}"
      
        results = npcs_test.get_report(format="json", start_date=ten_days_ago_str, end_date=today_str)
        self.assertEqual(test_utils.is_valid_report_json(results), True)

    # Successful report retrieval in email format
    def test_successful_report_retrieval_email(self):
        import sdk
        npcs_test = sdk.Neuropacs(server_url="https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox", api_key="generate_api_key", origin_type=test_utils.origin_type)
        npcs_test.connect()

        today = datetime.date.today()
        ten_days_ago = today - datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_ago_str = f"{ten_days_ago.month}/{ten_days_ago.day}/{ten_days_ago.year}"
      
        results = npcs_test.get_report(format="email", start_date=ten_days_ago_str, end_date=today_str)
        self.assertEqual(str(results), "Email sent successfully to kerrick@neuropacs.com.")

    # Invalid start date format in report retrieval
    def test_invalid_start_date_format_in_report_retrieval(self):
        import sdk
        npcs_test = sdk.Neuropacs(server_url="https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox", api_key="generate_api_key", origin_type=test_utils.origin_type)
        npcs_test.connect()

        today = datetime.date.today()
        today_str = f"{today.month}/{today.day}/{today.year}"
        
        with self.assertRaises(Exception) as context:
            npcs_test.get_report(format="txt", start_date="not_a_real_date", end_date=today_str)
        self.assertEqual(str(context.exception),"Report retrieval failed: Invalid date format (MM/DD/YYYY).")

    # Invalid end date format in report retrieval
    def test_invalid_end_date_format_in_report_retrieval(self):
        import sdk
        npcs_test = sdk.Neuropacs(server_url="https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox", api_key="generate_api_key", origin_type=test_utils.origin_type)
        npcs_test.connect()

        today = datetime.date.today()
        today_str = f"{today.month}/{today.day}/{today.year}"
        
        with self.assertRaises(Exception) as context:
            npcs_test.get_report(format="txt", start_date=today_str, end_date="not_a_real_date")
        self.assertEqual(str(context.exception),"Report retrieval failed: Invalid date format (MM/DD/YYYY).")

    # End date before start date in report retrieval
    def test_invalid_date_order_in_report_retrieval(self):
        import sdk
        npcs_test = sdk.Neuropacs(server_url="https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox", api_key="generate_api_key", origin_type=test_utils.origin_type)
        npcs_test.connect()

        today = datetime.date.today()
        ten_days_ago = today - datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_ago_str = f"{ten_days_ago.month}/{ten_days_ago.day}/{ten_days_ago.year}"
        
        with self.assertRaises(Exception) as context:
            npcs_test.get_report(format="txt", start_date=today_str, end_date=ten_days_ago_str)
        self.assertEqual(str(context.exception),"Report retrieval failed: start_date must not exceed end_date.")

    # End date exceeds current date in report retrieval
    def test_future_end_date_in_report_retrieval(self):
        import sdk
        npcs_test = sdk.Neuropacs(server_url="https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox", api_key="generate_api_key", origin_type=test_utils.origin_type)
        npcs_test.connect()

        today = datetime.date.today()
        ten_days_future = today + datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_future_str = f"{ten_days_future.month}/{ten_days_future.day}/{ten_days_future.year}"
        
        with self.assertRaises(Exception) as context:
            npcs_test.get_report(format="txt", start_date=today_str, end_date=ten_days_future_str)
        self.assertEqual(str(context.exception),"Report retrieval failed: Provided date must not exceed current date.")

    # Start date exceeds current date in report retrieval
    def test_future_start_date_in_report_retrieval(self):
        import sdk
        npcs_test = sdk.Neuropacs(server_url="https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox", api_key="generate_api_key", origin_type=test_utils.origin_type)
        npcs_test.connect()

        today = datetime.date.today()
        ten_days_future = today + datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_future_str = f"{ten_days_future.month}/{ten_days_future.day}/{ten_days_future.year}"
        
        with self.assertRaises(Exception) as context:
            npcs_test.get_report(format="txt", start_date=ten_days_future_str, end_date=today_str)
        self.assertEqual(str(context.exception),"Report retrieval failed: Provided date must not exceed current date.")

        
if __name__ == '__main__':
    unittest.main()