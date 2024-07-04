from sdk import Neuropacs

def main():
    api_key = "kDmOadtVXC1yZfST0cqJFapIMCeKZUT2rYHBF1kd"
    # api_key = "cdXVNIFzEUbSElTpoVoK4SyRrJ7Zj6n6Y6wgApIc"
    server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/v1"
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
    # order = npcs.new_job()
    # print(order)

    # # # UPLOAD A DATASET
    # datasetID = npcs.upload_dataset("../dicom_examples/DICOM_small", order, order, callback=lambda data: print(data))
    # print(datasetID)

    # # # START A JOB
    # job = npcs.run_job(product_id, "d0a8efaf-d5f0-4b4b-a600-40c477aa16eb")
    # print(job)

    # CHECK STATUS
    status = npcs.check_status("d0a8efaf-d5f0-4b4b-a600-40c477aa16eb")
    print(status)

    # # # GET RESULTS
    # results = npcs.get_results(result_format, "d9b5ad6c-818b-4d05-b772-80518a1f2c56")
    # print(results)

    

main()