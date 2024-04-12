from sdk import Neuropacs

def main():
    # api_key = "your_api_key"
    api_key = "m0ig54amrl87awtwlizcuji2bxacjm"
    server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/dev/"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "TXT"


    # PRINT CURRENT VERSION
    # version = Neuropacs.PACKAGE_VERSION

    # INITIALIZE NEUROPACS SDK
    # npcs = Neuropacs.init(server_url, server_url, api_key)
    npcs = Neuropacs(server_url, api_key)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)

    # # CREATE A NEW JOB
    order = npcs.new_job()
    print(order)

    # # UPLOAD A DATASET
    # upload = npcs.upload("../dicom_examples/DICOM_small/woo_I0", "test123", order)
    # print(upload)
    datasetID = npcs.upload_dataset("../dicom_examples/DICOM_small", None, None, callback=lambda data: print(f"Dataset ID: {data['datasetId']}, Progress: {data['progress']}%, Files Uploaded: {data['filesUploaded']}"))
    print(datasetID)

    # verUpl = npcs.validate_upload(["woo_I0", "woo_I2", "woo_I3", "woo_I4", "TEST234","woo_I7", "woo_I8", "woo_I9","woo_I10", "woo_I11"], "AHw8Wqpb2Ts8ffeTvlAR", "I2C1mIU8IsiFwkTZfpsd")
    # print(verUpl)

    # # # START A JOB
    # job = npcs.run_job(product_id, "Ri8vzdAXlWmiLgEV1JUC","dfjujor327nf415vubj7x")
    # print(job)

    # # CHECK STATUS
    # status = npcs.check_status("TEST", "dfjujor327nf415vubj7x")
    # print(status)

    # # # GET RESULTS
    # results = npcs.get_results(result_format, "TEST", "rnxor3q9euor9r088x0mnl")
    # print(results)

    

main()