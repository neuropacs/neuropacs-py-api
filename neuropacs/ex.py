from sdk import Neuropacs
import asyncio

def main():
    # api_key = "your_api_key"
    api_key = "m0ig54amrl87awtwlizcuji2bxacjm"
    server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/dev/"
    # socket_url = "wss://e3j5nzndo3.execute-api.us-east-2.amazonaws.com/dev/"
    # server_url = "http://localhost:3000"
    # socket_url = "ws://localhost:5000"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "TXT"


    # PRINT CURRENT VERSION
    # version = Neuropacs.PACKAGE_VERSION

    # INITIALIZE NEUROPACS SDK
    # npcs = Neuropacs.init(server_url, server_url, api_key)
    npcs = Neuropacs(server_url, server_url, api_key)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)

    # # CREATE A NEW JOB
    order = npcs.new_job()
    print(order)

    # # UPLOAD A DATASET
    datasetID = npcs.upload_dataset("../dicom_examples/06_001")
    print(datasetID)

    # # # START A JOB
    # job = npcs.run_job(product_id)
    # print(job)

    # # CHECK STATUS
    # status = npcs.check_status("TEST")

    # # GET RESULTS
    # results = npcs.get_results(result_format, "TEST")

main()