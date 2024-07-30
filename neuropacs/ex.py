from sdk import Neuropacs

def main():
    api_key = "" #!DELETE THIS
    server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/dev"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "JSON"

    # PRINT CURRENT VERSION
    # version = Neuropacs.PACKAGE_VERSION

    # INITIALIZE NEUROPACS SDK
    # npcs = Neuropacs.init(server_url, server_url, api_key)


    # for i in range(1000):
    #     try:
    npcs = Neuropacs(server_url, api_key)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)
        # except Exception as e:
        #     print(str(e))

    # # # # # # CREATE A NEW JOB
    order = npcs.new_job()
    print(order)

    # # # # # UPLOAD A DATASET
    # datasetID = npcs.upload_dataset("../dicom_examples/test_dataset", order, order, callback=lambda data: print(data))
    # print(datasetID)

    # # # START A JOB
    # job = npcs.run_job(product_id, "683abdf7-be60-4764-b35e-3bf396bdefd0")
    # print(job)

    # CHECK STATUS
    # status = npcs.check_status("0b183dd2-d07b-4ac9-a558-1dc3d51aea80")
    # print(status)

    # # # GET RESULTS
    results = npcs.get_results("JSON", "TEST")
    print(results)

    

main()