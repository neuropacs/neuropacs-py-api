import unittest
import test_utils
import time
import datetime
import neuropacs

class IntegrationTests(unittest.TestCase):

    '''
    Tests todo:
    - invalid url
    - admin key access to non admin job info (should succeed)
    - non admin key access to admin job info (should fail)
    - qc check in progress
    - incomplete upload?
    '''

    # neuropacs classes
    npcs_admin = None
    npcs_reg = None
    npcs_invalid_key = None
    npcs_no_usages = None
    npcs_invalid_url = None

    def setUp(self):
        """This method runs before each test"""
        self.npcs_admin = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.admin_key, origin_type=test_utils.origin_type)
        self.npcs_reg = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.reg_key, origin_type=test_utils.origin_type)
        self.npcs_invalid_key = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.invalid_key, origin_type=test_utils.origin_type)
        self.npcs_no_usages = neuropacs.init(server_url=test_utils.server_url, api_key=test_utils.no_usages_remaining_api_key, origin_type=test_utils.origin_type)
        self.npcs_invalid_url = neuropacs.init(server_url=test_utils.invalidServerUrl, api_key=test_utils.reg_key, origin_type=test_utils.origin_type)
    
    # Successful connection
    def test_successful_connection(self):
        conn = self.npcs_admin.connect()
        self.assertEqual(test_utils.is_valid_session_obj(conn), True)

    # Invalid API key
    def test_invalid_api_key(self):
        with self.assertRaises(Exception) as context:
            self.npcs_invalid_key.connect()
        self.assertEqual(str(context.exception),"Connection failed: API key not found.")

    # Successful order creation
    def test_successful_order_creation(self):
        self.npcs_admin.connect()
        order_id = self.npcs_admin.new_job()
        self.assertEqual(test_utils.is_valid_uuid4(order_id), True)

    # Missing connnection parameters
    def test_missing_connection_parameters(self):
        with self.assertRaises(Exception) as context:
            self.npcs_admin.connection_id = None
            self.npcs_admin.aes_key = None
            self.npcs_admin.new_job()
        self.assertEqual(str(context.exception),"Job creation failed: Missing session parameters, start a new session with 'connect()' and try again.")

    # Successful dataset upload
    def test_successful_dataset_upload(self):
        self.npcs_admin.connect()
        order_id = self.npcs_admin.new_job()
        upload_status = self.npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_local)
        self.assertEqual(upload_status, True)

    # Invalid dataset path
    def test_invalid_dataset_path(self):
        self.npcs_admin.connect()
        order_id = self.npcs_admin.new_job()
        with self.assertRaises(Exception) as context:
            self.npcs_admin.upload_dataset_from_path(order_id=order_id, path="/not/real")
        self.assertEqual(str(context.exception),"Error uploading dataset from path: Path not a directory.")

    # Invalid order ID
    def test_invalid_order_id_upload(self):
        self.npcs_admin.connect()
        with self.assertRaises(Exception) as context:
            self.npcs_admin.upload_dataset_from_path(order_id="no_real", path=test_utils.dataset_path_local)
        self.assertEqual(str(context.exception),"Error uploading dataset from path: Multipart upload initialization failed: Bucket not found.")

    # Successful job run
    def test_successful_job_run(self):
        self.npcs_admin.connect()
        order_id = self.npcs_admin.new_job()
        upload_status = self.npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_local_single)
        time.sleep(30)
        job = self.npcs_admin.run_job(order_id=order_id, product_name=test_utils.product_id)
        self.assertEqual(upload_status, True)
        self.assertEqual(job, 202)

    # Invalid order id
    def test_invalid_order_id(self):
        self.npcs_reg.connect()
        with self.assertRaises(Exception) as context:
            self.npcs_reg.run_job(test_utils.invalid_order_id, test_utils.product_id)
        self.assertEqual(str(context.exception),"Job run failed: Bucket not found.")

    # No API key usages remaining
    def test_no_api_key_usages_remaining(self):
        with self.assertRaises(Exception) as context:
            self.npcs_no_usages.connect()
            order_id = self.npcs_no_usages.new_job()
            self.npcs_no_usages.run_job(order_id=order_id, product_name=test_utils.product_id)
        self.assertEqual(str(context.exception),"Job run failed: No API key usages remaining.")

    # Invalid product ID
    def test_invalid_product(self):
        with self.assertRaises(Exception) as context:
            self.npcs_admin.connect()
            order_id = self.npcs_admin.new_job()
            self.npcs_admin.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_local_single)
            self.npcs_admin.run_job(order_id=order_id, product_name=test_utils.invalid_product_id)
        self.assertEqual(str(context.exception),"Job run failed: Product not found.")

    # Successful status check
    def test_successful_status_check(self):
        self.npcs_admin.connect()
        status = self.npcs_admin.check_status(order_id="TEST")
        self.assertEqual(test_utils.is_valid_status_obj(status), True)

    # Invalid order id in status check
    def test_invalid_order_id_in_status_check(self):
        self.npcs_admin.connect()
        with self.assertRaises(Exception) as context:
            status = self.npcs_admin.check_status(order_id="Not_Valid")
        self.assertEqual(str(context.exception),"Status check failed: Bucket not found.")

    # Successful result retrieval in txt format
    def test_successful_result_retrieval_txt(self):
        self.npcs_admin.connect()
        results = self.npcs_admin.get_results(order_id="TEST", format="txt")
        self.assertEqual(test_utils.is_valid_result_txt(results), True)

    # Successful result retrievel in json format
    def test_successful_result_retrieval_json(self):
        self.npcs_admin.connect()
        results = self.npcs_admin.get_results(order_id="TEST", format="JSON")
        self.assertEqual(test_utils.is_valid_result_json(results), True)

    # Successful result retrievel in features format
    def test_successful_result_retrieval_features(self):
        self.npcs_reg.connect()
        results = self.npcs_reg.get_results(order_id="TEST", format="features")
        self.assertEqual(test_utils.is_valid_result_txt(results), True)

    # Invalid result format
    def test_invalid_format_in_result_retrieval(self):
        self.npcs_admin.connect()
        with self.assertRaises(Exception) as context:
            results = self.npcs_admin.get_results(order_id="TEST", format="INVALID")
        self.assertEqual(str(context.exception), "Result retrieval failed: Invalid format.")

    # Successfully run QC check (will fail)
    def test_successful_qc_check(self):
        self.npcs_reg.connect()
        order_id = self.npcs_reg.new_job()
        self.npcs_reg.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_local)
        time.sleep(120)
        qc = self.npcs_reg.qc_check(order_id, "txt")
        self.assertIn("QC FAILED", qc)

    # Qc check invalid format
    def test_invalid_format_qc_check(self):
        self.npcs_reg.connect()
        order_id = self.npcs_reg.new_job()
        with self.assertRaises(Exception) as context:
            self.npcs_reg.qc_check(order_id, "not_real")
        self.assertEqual(str(context.exception), "QC check failed: Invalid format.")

    # Qc check no dataset found
    def test_no_dataset_qc_check(self):
        self.npcs_reg.connect()
        order_id = self.npcs_reg.new_job()
        self.npcs_reg.api_key = None
        with self.assertRaises(Exception) as context:
            self.npcs_reg.qc_check(order_id, "txt")
        self.assertEqual(str(context.exception), "QC check failed: No dataset found. Upload a dataset before running QC.")
    
    # Qc Check dataset in use
    def test_dataset_in_use_qc_check(self):
        self.npcs_reg.connect()
        order_id = self.npcs_reg.new_job()
        self.npcs_reg.upload_dataset_from_path(order_id=order_id, path=test_utils.dataset_path_local)
        with self.assertRaises(Exception) as context:
            self.npcs_reg.qc_check(order_id, "txt")
        self.assertIn(str(context.exception), [
            "QC check failed: Dataset in use, try again later.",
            "QC check failed: QC in progress."
        ])

    # Successful report retrieval in txt format
    def test_successful_report_retrieval_txt(self):
        self.npcs_reg.connect()

        today = datetime.date.today()
        ten_days_ago = today - datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_ago_str = f"{ten_days_ago.month}/{ten_days_ago.day}/{ten_days_ago.year}"
      
        results = self.npcs_reg.get_report(format="txt", start_date=ten_days_ago_str, end_date=today_str)
        self.assertEqual(test_utils.is_valid_report_txt(results), True)

    # Successful report retrieval in json format
    def test_successful_report_retrieval_json(self):
        self.npcs_reg.connect()

        today = datetime.date.today()
        ten_days_ago = today - datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_ago_str = f"{ten_days_ago.month}/{ten_days_ago.day}/{ten_days_ago.year}"
      
        results = self.npcs_reg.get_report(format="json", start_date=ten_days_ago_str, end_date=today_str)
        self.assertEqual(test_utils.is_valid_report_json(results), True)

    # Successful report retrieval in email format
    def test_successful_report_retrieval_email(self):
        self.npcs_reg.connect()

        today = datetime.date.today()
        ten_days_ago = today - datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_ago_str = f"{ten_days_ago.month}/{ten_days_ago.day}/{ten_days_ago.year}"
      
        results = self.npcs_reg.get_report(format="email", start_date=ten_days_ago_str, end_date=today_str)
        self.assertIn("Email sent successfully to", results)

    # Invalid start date format in report retrieval
    def test_invalid_start_date_format_in_report_retrieval(self):
        self.npcs_reg.connect()

        today = datetime.date.today()
        today_str = f"{today.month}/{today.day}/{today.year}"
        
        with self.assertRaises(Exception) as context:
            self.npcs_reg.get_report(format="txt", start_date="not_a_real_date", end_date=today_str)
        self.assertEqual(str(context.exception),"Report retrieval failed: Invalid date format (MM/DD/YYYY).")

    # Invalid end date format in report retrieval
    def test_invalid_end_date_format_in_report_retrieval(self):
        self.npcs_reg.connect()

        today = datetime.date.today()
        today_str = f"{today.month}/{today.day}/{today.year}"
        
        with self.assertRaises(Exception) as context:
            self.npcs_reg.get_report(format="txt", start_date=today_str, end_date="not_a_real_date")
        self.assertEqual(str(context.exception),"Report retrieval failed: Invalid date format (MM/DD/YYYY).")

    # End date before start date in report retrieval
    def test_invalid_date_order_in_report_retrieval(self):
        self.npcs_reg.connect()

        today = datetime.date.today()
        ten_days_ago = today - datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_ago_str = f"{ten_days_ago.month}/{ten_days_ago.day}/{ten_days_ago.year}"
        
        with self.assertRaises(Exception) as context:
            self.npcs_reg.get_report(format="txt", start_date=today_str, end_date=ten_days_ago_str)
        self.assertEqual(str(context.exception),"Report retrieval failed: start_date must not exceed end_date.")

    # End date exceeds current date in report retrieval
    def test_future_end_date_in_report_retrieval(self):
        self.npcs_reg.connect()

        today = datetime.date.today()
        ten_days_future = today + datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_future_str = f"{ten_days_future.month}/{ten_days_future.day}/{ten_days_future.year}"
        
        with self.assertRaises(Exception) as context:
            self.npcs_reg.get_report(format="txt", start_date=today_str, end_date=ten_days_future_str)
        self.assertEqual(str(context.exception),"Report retrieval failed: Provided date must not exceed current date.")

    # Start date exceeds current date in report retrieval
    def test_future_start_date_in_report_retrieval(self):
        self.npcs_reg.connect()

        today = datetime.date.today()
        ten_days_future = today + datetime.timedelta(days=10)
        today_str = f"{today.month}/{today.day}/{today.year}"
        ten_days_future_str = f"{ten_days_future.month}/{ten_days_future.day}/{ten_days_future.year}"
        
        with self.assertRaises(Exception) as context:
            self.npcs_reg.get_report(format="txt", start_date=ten_days_future_str, end_date=today_str)
        self.assertEqual(str(context.exception),"Report retrieval failed: Provided date must not exceed current date.")

        
if __name__ == '__main__':
    unittest.main()