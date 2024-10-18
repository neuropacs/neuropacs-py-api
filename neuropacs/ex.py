from sdk import Neuropacs

def main():
    api_key = "" #!DELETE THIS
    server_url = ""
    product_id = "Atypical/MSAp/PSP-v1.0"
    result_format = "JSON"
    origin_type = "example"

    # INITIALIZE NEUROPACS SDK
    npcs = Neuropacs(server_url, api_key, origin_type)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)

    # CREATE A NEW JOB
    order = npcs.new_job()
    print(order)

    # UPLOAD A DATASET
    datasetID = npcs.upload_dataset("", order, order, callback=lambda data: print(data))
    print(datasetID)

    # START A JOB
    job = npcs.run_job(product_id, order)
    print(job)

    # CHECK STATUS
    status = npcs.check_status("")
    print(status)

    # # # # # GET RESULTS
    results = npcs.get_results(result_format, "")
    print(results)

    

main()