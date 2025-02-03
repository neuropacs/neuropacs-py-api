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
qc_format = "CSV"
origin_type = "my_application"

# INITIALIZE NEUROPACS API
npcs = neuropacs.init(server_url=server_url, api_key=api_key, origin_type=origin_type)

# CONNECT TO NEUROPACS
connection = npcs.connect()

# CREATE A NEW JOB
order_id = npcs.new_job()

# UPLOAD A DATASET FROM PATH
upload_status = npcs.upload_dataset_from_path(order_id=order_id,  path="/path/to/dataset/")

# RUN QUALITY CONTROL/COMPLIANCE CHECK ON DATASET (not required)
qc_check = npcs.qc_check(order_id=order_id, format=qc_format)

# START A JOB
# --> Valid product_name options: Atypical/MSAp/PSP-v1.0
job_start_status = npcs.run_job(order_id=order_id, product_name=product_name)

# CHECK JOB STATUS
job_status = npcs.check_status(order_id=order_id)

# RETRIEVE JOB RESULTS
# --> Valid prediction_format options: TXT, PDF, XML, PNG
job_results = npcs.get_results(order_id=order_id, format=prediction_format)
```

### Generate API Key Usage Report

```py
import neuropacs

api_key = "api_key"
server_url = "neuropacs_url"
format = "csv" # Valid options include "txt", "json", and "email"
start_date = "10/1/2024" # Must be in mM/dD/YYYY format
end_date = "12/1/2025" # Must be in mM/dD/YYYY format

# INITIALIZE NEUROPACS API (get_report API will use the API key specified here)
npcs = neuropacs.init(server_url=server_url, api_key=api_key, origin_type=origin_type)

# CONNECT TO NEUROPACS
connection = npcs.connect()

# GET REPORT
# --> If 'email' format used, an email will be sent to the admin user associated with the specified key
usage_report = get_report(format=format, start_date=start_datae, end_date=end_date)
```

### DICOMweb WADO-RS Integration

```py
# DEFINE DICOMweb PARAMETERS
wado_url = "http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/rs"
study_uid = "1.3.12.2.1107.5.2.32.35162.30000022041820573832300000043"
username = "username"
password = "password"

# UPLOAD DATASET FROM DICOMweb WADO-RS
upload = npcs.upload_dataset_from_dicom_web(
  order_id=order_id,
  wado_url=wado_url,
  study_uid=study_uid,
  username=username,
  password=password,
  callback=lambda data: print(data) # optional progress callback
)
```

## Authors

Kerrick Cavanaugh - kerrick@neuropacs.com

## Version History

- 1.0.0
  - Initial Release
  - See [release history](https://pypi.org/project/neuropacs/#history)
- 1.8.6
  - Latest Stable Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
