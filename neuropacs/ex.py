from sdk import Neuropacs

def main():
    api_key = "Wa02MlTrzgaFHEwIZVngda916g6893M7apqvQTFc" #!DELETE THIS
    # server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/dev"
    server_url = "https://aw75e2na5m.execute-api.us-east-1.amazonaws.com/dev"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "JSON"
    origin_type = "my_application"

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

    # # # # CREATE A NEW JOB
    # order = npcs.new_job()
    # print(order)

    # # # # # # # UPLOAD A DATASET
    # datasetID = npcs.upload_dataset("/Users/kerrickcavanaugh/Desktop/sample data/DICOM_small", order, order, callback=lambda data: print(data))
    # print(datasetID)

    # # # # # START A JOB
    # job = npcs.run_job(product_id, order)
    # print(job)

    # # # CHECK STATUS
    status = npcs.check_status("0a90258e-e0bf-4697-bfbc-37ee6147c1ab")
    print(status)

    # # # # # GET RESULTS
    # results = npcs.get_results("JSON", "b863e635-074b-400d-bc6f-226a15046eed")
    # print(results)

    

main()