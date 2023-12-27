import neuropacs
# from neuropacs.sdk import Neuropacs

def main():
    # api_key = "your_api_key"
    api_key = "m0ig54amrl87awtwlizcuji2bxacjm"
    # server_url = "http://your_server_url:5000"
    server_url = "http://ec2-3-142-212-32.us-east-2.compute.amazonaws.com:5000"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "JSON"

    # PRINT CURRENT VERSION
    version = neuropacs.PACKAGE_VERSION

    # INITIALIZE NEUROPACS SDK
    npcs = neuropacs.init(server_url, api_key)

    # CREATE A CONNECTION   
    npcs.connect()

    # CREATE A NEW JOB
    npcs.new_job()

    # UPLOAD A DATASET
    npcs.upload_dataset("../dicom_examples/06_001")

    # START A JOB
    job = npcs.run_job(product_id)

    # CHECK STATUS
    status = npcs.check_status()

    # GET RESULTS
    results = npcs.get_results(result_format)


main()