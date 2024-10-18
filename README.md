[![Integration Tests](https://github.com/neuropacs/neuropacs-py-api/actions/workflows/ci.yml/badge.svg)](https://github.com/neuropacs/neuropacs-py-api/actions/workflows/ci.yml)

# neuropacs™ Python API

Connect to neuropacs™ diagnostic capabilities with our Python API.

## Getting Started

### Installation

```bash
pip install neuropacs
```

### Usage

```py
import neuropacs

api_key = "your_api_key"
server_url = "https://your_neuropacs_url"
product_name = "Atypical/MSAp/PSP-v1.0"
prediction_format = "XML"
origin_type = "my_application"

# INITIALIZE NEUROPACS API
npcs = neuropacs.init(server_url=server_url, api_key=api_key, origin_type=origin_type)

# CONNECT TO NEUROPACS
connection = npcs.connect()

# CREATE A NEW JOB
order_id = npcs.new_job()

# UPLOAD A DATASET
# --> dataset_path must be a valid path to a dataset <String>
# --> dataset_id param is optional (only will be generated for you if you do not specify it). We recommend using the orderId as the datasetId for simplicity
upload_status = npcs_admin.upload_dataset("/path/to/dataset/", order_id=order_id, dataset_id=order_id)

# START A JOB
# --> Valid product_name options: Atypical/MSAp/PSP-v1.0
job_start_status = npcs.run_job(product_name=product_name, order_id=order_id)

# CHECK JOB STATUS
job_status = npcs.check_status(order_id=order_id)

# RETRIEVE JOB RESULTS
# --> Valid prediction_format options: TXT, PDF, XML, PNG
job_results = npcs.get_results(prediction_format=prediction_format, order_id=order_id)
```

## Authors

Kerrick Cavanaugh - kerrick@neuropacs.com

## Version History

- 1.0.0
  - Initial Release
  - See [release history](https://pypi.org/project/neuropacs/#history)

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
