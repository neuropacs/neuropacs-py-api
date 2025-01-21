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

    report = npcs.get_report("email", "10/1/2024", "1/15/2025")
    print(report)

    # # # CREATE A NEW JOB
    # order = npcs.new_job()
    # print(order)

    # print(npcs.check_status("TEST"))

main()



