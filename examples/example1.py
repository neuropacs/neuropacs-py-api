import neuropacs

def main():
    api_key = "your_api_key"
    server_url = "http://your_neuropacs_url:5000"
    product_id = "PD/MSA/PSP-v1.0"

    # PRINT CURRENT VERSION
    version = neuropacs.PACKAGE_VERSION
    print(version)

    # # INITIALIZE NEUROPACS SDK
    npcs = neuropacs.init(api_key, server_url)

    # # # # GENERATE AN AES KEY
    aes_key = npcs.generate_aes_key()

    # # # # # CONNECT TO NEUROPACS
    connection_id = npcs.connect(api_key,aes_key)

    # # # # # CREATE A NEW JOB
    order_id = npcs.new_job(connection_id, aes_key)

    print(f"connection_id: {connection_id}")
    print(f"aes_key: {aes_key}")
    print(f"productID: {product_id}")
    print(f"orderID: {order_id}")

    # # # # #UPLOAD AN IMAGE
    npcs.upload_dataset("./dicom_examples/06_001",order_id,connection_id, aes_key)


    # connection_id: 42b2de6a603577ac4d7ff5309149d82c
    # aes_key: 74v4UiZEfqZ3T150f2Q+/Q==
    # productID: PD/MSA/PSP-v1.0
    # orderID: jzvaP40B3wKgQBe0v0EH

    # # # #START A JOB
    job = npcs.run_job(product_id, order_id, connection_id, aes_key)
    print(job)
    # job = npcs.run_job(product_id, "jzvaP40B3wKgQBe0v0EH", "42b2de6a603577ac4d7ff5309149d82c", "74v4UiZEfqZ3T150f2Q+/Q==")
    # print(job)/

    #CHECK STATUS
    # status = npcs.check_status("jzvaP40B3wKgQBe0v0EH", "42b2de6a603577ac4d7ff5309149d82c", "74v4UiZEfqZ3T150f2Q+/Q==")
    # status = npcs.check_status("tBgLD2XjXpNpdxs2L7Pv", connection_id , aes_key)
    # print(status)

    #GET RESULTS
    # results = npcs.get_results(connection_id, aes_key, order_id, "TXT")
    # results = npcs.get_results("TXT", "McIU9XjLZOrPo265y9v1","57bc28b9c10cb9577b07deba4b6ff866", "/sgHRTqeE10eyNtlNKejng==")
    # print(results)/


main()