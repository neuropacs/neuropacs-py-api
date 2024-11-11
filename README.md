[![Integration Tests](https://github.com/neuropacs/neuropacs-py-api/actions/workflows/ci.yml/badge.svg)](https://github.com/neuropacs/neuropacs-py-api/actions/workflows/ci.yml)
![CodeQL](https://github.com/neuropacs/neuropacs-py-api/actions/workflows/codeql-analysis.yml/badge.svg)

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

api_key = "api_key"
server_url = "neuropacs_url"
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
upload_status = npcs_admin.upload_dataset_from_path(order_id=order_id,  path="/path/to/dataset/")

# START A JOB
# --> Valid product_name options: Atypical/MSAp/PSP-v1.0
job_start_status = npcs.run_job(order_id=order_id, product_name=product_name)

# CHECK JOB STATUS
job_status = npcs.check_status(order_id=order_id)

# RETRIEVE JOB RESULTS
# --> Valid prediction_format options: TXT, PDF, XML, PNG
job_results = npcs.get_results(order_id=order_id, prediction_format=prediction_format)
```

## Authors

Kerrick Cavanaugh - kerrick@neuropacs.com

## Version History

- 1.0.0
  - Initial Release
  - See [release history](https://pypi.org/project/neuropacs/#history)

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
