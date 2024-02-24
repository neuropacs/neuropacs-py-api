# import neuropacs
from neuropacs.sdk import Neuropacs

def main():
    # api_key = "your_api_key"
    api_key = "m0ig54amrl87awtwlizcuji2bxacjm"
    server_url = "http://ec2-18-218-48-101.us-east-2.compute.amazonaws.com:5000"
    # server_url = "http://localhost:5000"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "TXT"


    # PRINT CURRENT VERSION
    # version = neuropacs.PACKAGE_VERSION
    npcs = Neuropacs(server_url, api_key)

    # INITIALIZE NEUROPACS SDK
    # npcs = neuropacs.init(server_url, api_key)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)

    # # CREATE A NEW JOB
    # order = npcs.new_job()
    # print(order)

    # # # UPLOAD A DATASET
    # npcs.upload_dataset("../dicom_examples/DICOM_small")

    # # # START A JOB
    # job = npcs.run_job(product_id)
    # print(job)

    # # CHECK STATUS
    status = npcs.check_status("TEST")
    print(status)

    # GET RESULTS
    results = npcs.get_results(result_format, "TEST")
    print(results)


main()