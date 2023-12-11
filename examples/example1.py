import neuropacs

def main():
    api_key = "your_api_key"
    server_url = "http://your_neuropacs_url:5000"
    product_id = "PD/MSA/PSP-v1.0"
    result_format = "TXT"

    # PRINT CURRENT VERSION
    version = neuropacs.PACKAGE_VERSION

    # INITIALIZE NEUROPACS SDK
    npcs = neuropacs.init(api_key, server_url)

    # GENERATE AN AES KEY
    aes_key = npcs.generate_aes_key()

    # CONNECT TO NEUROPACS
    connection_id = npcs.connect(api_key,aes_key)

    # CREATE A NEW JOB
    order_id = npcs.new_job(connection_id, aes_key)

    # UPLOAD AN IMAGE
    npcs.upload_dataset("./dicom_examples/06_001",order_id,connection_id, aes_key)

    # START A JOB
    job = npcs.run_job(product_id, order_id, connection_id, aes_key)

    # CHECK STATUS
    status = npcs.check_status(order_id, connection_id , aes_key)

    #GET RESULTS
    results = npcs.get_results(connection_id, aes_key, order_id, result_format)


main()