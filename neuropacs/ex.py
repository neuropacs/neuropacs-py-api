from sdk import Neuropacs

def main():
    api_key = "lllLRG7RSb3BCn4sVHBrT8jX9rVgeWmeaAkU8sDR" #!DELETE THIS
    server_url = "https://jdfkdttvlf.execute-api.us-east-1.amazonaws.com/prod"
    product_id = "Atypical/MSAp/PSP-v1.0"
    result_format = "JSON"
    origin_type = "example"
    dicom_path = "path/to/dicom"

    # INITIALIZE NEUROPACS SDK
    npcs = Neuropacs(server_url, api_key, origin_type)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)

    # CREATE A NEW JOB
    order = npcs.new_job()
    print(order)

    # UPLOAD A DATASET
    datasetID = npcs.upload_dataset(dicom_path, order, order, callback=lambda data: print(data))
    print(datasetID)

    # START A JOB
    job = npcs.run_job(product_id, order)
    print(job)

    # CHECK STATUS
    status = npcs.check_status(order)
    print(status)

    # GET RESULTS
    results = npcs.get_results(result_format, order)
    print(results)

    

main()