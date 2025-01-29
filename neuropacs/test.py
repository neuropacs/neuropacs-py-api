from sdk import Neuropacs
# import sdk

def main():
    api_key = "generate_api_key" #!DELETE THIS
    server_url = "https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox"
    product_id = "Atypical/MSAp/PSP-v1.0"
    result_format = "PNG"
    origin_type = "example"
    dicom_path = "/Users/kerrickcavanaugh/Desktop/sample data/06_001"

    # INITIALIZE NEUROPACS SDK
    npcs = Neuropacs(server_url, api_key, origin_type)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)

    # # # # # # CREATE A NEW JOB
    # order = npcs.new_job()
    # print(order)

    # # UPLOAD A DATASET
    # upload = npcs.upload_dataset_from_path(order, dicom_path, callback=lambda data: print(data))
    # print(upload)

    qc = npcs.qc_check(order_id="a3516091-8424-4e5c-a89b-4aa20cf5cc7d", format="json")
    print(qc)


main()



