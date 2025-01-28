from sdk import Neuropacs

def main():
    api_key = "generate_api_key" #!DELETE THIS
    server_url = "https://ud7cvn39n4.execute-api.us-east-1.amazonaws.com/sandbox"
    origin_type = "example"

    # INITIALIZE NEUROPACS SDK
    npcs = Neuropacs(server_url, api_key, origin_type)

    # CREATE A CONNECTION   
    conn = npcs.connect()
    print(conn)


    # CREATE A NEW JOB
    order = npcs.new_job()
    print(order)

    upload = npcs.upload_dataset_from_path(order, "/Users/kerrickcavanaugh/Desktop/sample data/06_001", callback=lambda data: print(data))
    print(upload)

    # report = npcs.get_report("email", "10/1/2024", "1/15/2025")
    # print(report)

  

    # print(npcs.check_status("TEST"))

main()



