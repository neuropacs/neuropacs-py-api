# from sdk import Neuropacs
import neuropacs

def main():
    # api_key = "your_api_key"
    api_key = "m0ig54amrl87awtwlizcuji2bxacjm"
    server_url = "https://sl3tkzp9ve.execute-api.us-east-2.amazonaws.com/dev/"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "JSON"


    # PRINT CURRENT VERSION
    # version = Neuropacs.PACKAGE_VERSION

    # INITIALIZE NEUROPACS SDK
    npcs = neuropacs.init(server_url, api_key)
    # npcs = neuropacs(server_url, api_key)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)

    # # # # CREATE A NEW JOB
    order = npcs.new_job()
    print(order)

    # UPLOAD A DATASET
    # upload = npcs.upload("../dicom_examples/DICOM_small/woo_I0", "test123", order)
    # print(upload)
    datasetID = npcs.upload_dataset("../dicom_examples/DTI_1", order, order, callback=lambda data: print(data))
    print(datasetID)
    # datasetID = npcs.upload_dataset("../dicom_examples/06_001", order, order)

    # verUpl = npcs.validate_upload("../dicom_examples/DTI_1", "1150edbd-f26b-44c5-adba-49ada9ba9cfb", "1150edbd-f26b-44c5-adba-49ada9ba9cfb", callback=lambda data: print(data))
    # print(verUpl)

    # # # START A JOB
    # job = npcs.run_job(product_id, "e7d6902d-b49f-4dae-9a41-4fe8cf510aab","e7d6902d-b49f-4dae-9a41-4fe8cf510aab")
    # print(job)

    # # # CHECK STATUS
    # status = npcs.check_status("e7d6902d-b49f-4dae-9a41-4fe8cf510aab", "e7d6902d-b49f-4dae-9a41-4fe8cf510aab")
    # print(status)

    # # # # GET RESULTS
    # results = npcs.get_results(result_format, "WgcvoJQk3xFNiOPMoPZ6", "WgcvoJQk3xFNiOPMoPZ6")
    # print(results)

    

main()