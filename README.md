[![Integration Tests](https://github.com/neuropacs/neuropacs-py-api/actions/workflows/ci.yml/badge.svg)](https://github.com/neuropacs/neuropacs-py-api/actions/workflows/ci.yml)

# neuropacs™ Python API

Connect to neuropacs diagnostic capabilities with our Python API.

### Installation

```bash
pip install neuropacs
```

### Usage

```py
import neuropacs

api_key = "your_api_key"
server_url = "https://your_neuropacs_url"
product_id = "PD/MSA/PSP-v1.0"
prediction_format = "XML"

# PRINT CURRENT VERSION
version = neuropacs.PACKAGE_VERSION

#INITIALIZE NEUROPACS API
npcs = neuropacs.init(server_url=server_url, api_key=api_key)

#CONNECT TO NEUROPACS
connection = npcs.connect()

#CREATE A NEW JOB
order_id = npcs.new_job()

#UPLOAD AN IMAGE
# --> data must be a valid path <String> or byte array <Bytes>
# --> order_id param is optional
upload_status = npcs.upload(data)

#UPLOAD A DATASET
# --> dataset_path must be a valid path to a dataset <String>
# --> order_id param is optional
upload_status = npcs.upload_dataset(dataset_path)

#START A JOB
# --> Valid product_id options: PD/MSA/PSP-v1.0
# --> order_id param is optional
job_start_status = npcs.run_job(product_id)

#CHECK JOB STATUS
# --> order_id param is optional
job_status = npcs.check_status()

#RETRIEVE JOB RESULTS
# --> Valid prediction_format options: TXT, PDF, XML, JSON, DICOMSR
# --> order_id param is optional
job_results = npcs.get_results(prediction_format)
```

## Authors

Kerrick Cavanaugh - kerrick@neuropacs.com

## Version History

- 1.3.9
  - Initial Release
  - See [release history](https://pypi.org/project/neuropacs/#history)

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
