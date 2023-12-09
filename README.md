# NeuroPACS Python SDK

## Install neuropacs from pip

```bash
pip install neuropacs
```

## Usage

```py
import neuropacs

api_key = "your_api_key"
server_url = "https://your_neuropacs_url"
product_id = "PD/MSA/PSP-v1.0"
prediction_format = "XML"

# PRINT CURRENT VERSION
version = neuropacs.PACKAGE_VERSION

#INITIALIZE NEUROPACS SDK
npcs = neuropacs.init(api_key, server_url)

#GENERATE AN AES KEY
aes_key = npcs.generate_aes_key()

#CONNECT TO NEUROPACS
connection_id = npcs.connect(api_key, aes_key)

#CREATE A NEW JOB
order_id = npcs.new_job(connection_id, aes_key)

#UPLOAD AN IMAGE
# --> data must be a valid path <String> or byte array <Bytes>
upload_status = npcs.upload(data, order_id, connection_id, aes_key)

#UPLOAD A DATASET
# --> dataset_path must be a valid path to a dataset <String>
upload_status = npcs.upload_dataset(dataset_path,connection_id, order_id, aes_key)

#START A JOB
# --> Valid product_id options: PD/MSA/PSP-v1.0
job_start_status = npcs.run_job(connection_id, aes_key, product_id, order_id)

#CHECK JOB STATUS
job_status = npcs.check_status(order_id, connection_id, aes_key)

#RETRIEVE JOB RESULTS
# --> Valid prediction_format options: TXT, PDF, XML, JSON, DICOMSR
job_results = npcs.get_results(prediction_format, order_id, connection_id, aes_key)
```
