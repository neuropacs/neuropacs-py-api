from sdk import Neuropacs

def main():
    # api_key = "your_api_key"
    api_key = "m0ig54amrl87awtwlizcuji2bxacjm"
    server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/v2/"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "JSON"


    # PRINT CURRENT VERSION
    # version = Neuropacs.PACKAGE_VERSION

    # INITIALIZE NEUROPACS SDK
    # npcs = Neuropacs.init(server_url, server_url, api_key)
    npcs = Neuropacs(server_url, api_key)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)

    # # # # CREATE A NEW JOB
    order = npcs.new_job()
    print(order)

    # # # # UPLOAD A DATASET
    # upload = npcs.upload("../dicom_examples/DICOM_small/woo_I0", "test123", order)
    # print(upload)
    datasetID = npcs.upload_dataset("../dicom_examples/DICOM_small", order, order, callback=lambda data: print(data))
    print(datasetID)

    # verUpl = npcs.validate_upload(["woo_I0", "woo_I2", "woo_I3", "woo_I4","woo_I7", "woo_I8", "woo_I9","woo_I10", "woo_I11"], "ROBRg7N2xj0o2w4Gpmoy", "CH5uWzAZoiHB7AtemEqK")
    # print(verUpl)

    # # # START A JOB
    # job = npcs.run_job(product_id, "Ri8vzdAXlWmiLgEV1JUC","dfjujor327nf415vubj7x")
    # print(job)

    # # # CHECK STATUS
    # status = npcs.check_status("TEST", "WgcvoJQk3xFNiOPMoPZ6")
    # print(status)

    # # # # GET RESULTS
    # results = npcs.get_results(result_format, "WgcvoJQk3xFNiOPMoPZ6", "WgcvoJQk3xFNiOPMoPZ6")
    # print(results)

    

main()