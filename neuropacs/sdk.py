# neuropacs Python API v1.8.5
# (c) 2024 neuropacs
# Released under the MIT License.

import os
import requests
import json
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64
import zipfile
import io
import uuid
import time
from datetime import datetime
from dicomweb_client.api import DICOMwebClient
from Crypto.Cipher import AES
from functools import wraps
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

class Neuropacs:
    def __init__(self, server_url, api_key, origin_type="API"):
        """
        neuropacs constructor
        """
        self.server_url = server_url
        self.api_key = api_key
        self.origin_type = origin_type
        self.connection_id = None
        self.aes_key = None
        self.order_id = None
        self.max_zip_size = 15 * 1024 * 1024 # 15MB max zip file size

    # Private methods
    def __generate_aes_key(self):
        """Generate an 16-byte AES key for AES-CTR encryption.

        :return: AES key encoded as a base64 string.
        """
        aes_key = get_random_bytes(16)
        aes_key_base64 = base64.b64encode(aes_key).decode('utf-8')
        return aes_key_base64

    def __oaep_encrypt(self, plaintext):
        """
        OAEP encrypt plaintext.

        :param str/JSON plaintext: Plaintext to be encrypted.

        :return: Base64 string OAEP encrypted ciphertext
        """

        try:
            plaintext = json.dumps(plaintext)
        except:
            if not isinstance(plaintext, str):
                raise Exception({"neuropacsError": "Plaintext must be a string or JSON!"})   
    
        # get public key of server
        PUBLIC_KEY = self.get_public_key().replace('\\n', '\n').strip()

        PUBLIC_KEY = PUBLIC_KEY.encode('utf-8')

        # Deserialize the public key from PEM format
        public_key = serialization.load_pem_public_key(PUBLIC_KEY)

        # Encrypt the plaintext using OAEP
        ciphertext = public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        ciphertext_key_base64 = base64.b64encode(ciphertext).decode('utf-8')

        # Return the ciphertext as bytes
        return ciphertext_key_base64

    def __encrypt_aes_ctr(self, plaintext, format_in, format_out):
        """AES CTR encrypt plaintext

        :param JSON/str/bytes plaintext: Plaintext to be encrypted.
        :param str format_in: format of plaintext. Defaults to "string".
        :param str format_out: format of ciphertext. Defaults to "string".

        :return: Encrypted ciphertext in requested format_out.
        """        

        plaintext_bytes = ""

        try:
            if format_in == "string" and isinstance(plaintext, str):
                plaintext_bytes = plaintext.encode("utf-8")
            elif format_in == "bytes" and isinstance(plaintext,bytes):
                plaintext_bytes = plaintext
            elif format_in == "json":
                plaintext_json = json.dumps(plaintext)
                plaintext_bytes = plaintext_json.encode("utf-8")
            else:
                raise Exception({"neuropacsError": "Invalid plaintext format!"})
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError'])
            else:   
                raise Exception("Invalid plaintext format!")

        try:
            aes_key_bytes = base64.b64decode(self.aes_key)

            padded_plaintext = pad(plaintext_bytes, AES.block_size)

            # generate IV
            iv = get_random_bytes(16)

            # Create an AES cipher object in CTR mode
            cipher = AES.new(aes_key_bytes, AES.MODE_CTR, initial_value=iv, nonce=b'')

            # Encrypt the plaintext
            ciphertext = cipher.encrypt(padded_plaintext)

            # Combine IV and ciphertext
            encrypted_data = iv + ciphertext

            encryped_message = ""

            if format_out == "string":
                encryped_message = base64.b64encode(encrypted_data).decode('utf-8')
            elif format_out == "bytes":
                encryped_message = encrypted_data

            return encryped_message

        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError']) 
            else:
                raise Exception("AES encryption failed!")   

    def __decrypt_aes_ctr(self, encrypted_data, format_out):
        """AES CTR decrypt ciphertext.

        :param str ciphertext: Ciphertext to be decrypted.
        :param str format_out: Format of plaintext. Default to "string".

        :return: Plaintext in requested format_out.
        """

        try:

            aes_key_bytes = base64.b64decode(self.aes_key)

            # Decode the base64 encoded encrypted data
            encrypted_data = base64.b64decode(encrypted_data)

            # Extract IV and ciphertext
            iv = encrypted_data[:16]

            ciphertext = encrypted_data[16:]

            # Create an AES cipher object in CTR mode
            cipher = AES.new(aes_key_bytes, AES.MODE_CTR, initial_value=iv, nonce=b'')

            # Decrypt the ciphertext and unpad the result
            decrypted = cipher.decrypt(ciphertext)

            if format_out == "json":
                decrypted_data = decrypted.decode("utf-8")
                return json.loads(decrypted_data)
            elif format_out == "string":
                decrypted_data = decrypted.decode("utf-8")
                return decrypted_data
            elif format_out == "bytes":
                image_bytes =  bytes(decrypted)
                return io.BytesIO(image_bytes)

        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError']) 
            else:
                raise Exception("AES decryption failed!")

    def __ensure_unique_name(self, file_set, filename):
        """
        Ensures filenames are unique (some scanners produce duplicate filenames)

        :param set file_set: Set of existing file names
        :param str filename: File name to be added

        :return: New unique filename
        """
        hasExt = False
        if '.' in filename and not filename.startswith('.'):
            hasExt = True

        base_name = filename.rsplit('.', 1)[0] if hasExt else filename
        extension = filename.rsplit('.', 1)[-1] if hasExt else ""
        counter = 1

        new_name = filename

        while new_name in file_set:
            new_name = f"{base_name}_{counter}.{extension}" if hasExt else f"{base_name}_{counter}"
            counter += 1

        file_set.add(new_name)

        return new_name

    def __generate_unique_uuid(self):
        """
        Generate a random v4 uuid

        :return: V4 UUID string
        """
        return str(uuid.uuid4())

    def __read_file_contents(self, file_path):
        """
        Read file conents of file at file_path

        :param str file_path Path to the file to be read

        :return: File contents in bytes
        """
        with open(file_path, 'rb') as file:
            contents = file.read()
        return contents

    def __retry_request(max_retries=3, delay=1):
        """
        A decorator to retry AWS request-based function multiple times if it fails.
        
        :param max_retries: Maximum number of retries before giving up.
        :param delay: Delay in seconds between retries.
        """
        def decorator(func):
            @wraps(func) # better for API implementation
            def wrapper(*args, **kwargs):
                attempt = 0
                while attempt < max_retries:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempt += 1
                        if attempt == max_retries:
                            # All attempts failed
                            raise
                        time.sleep(delay)
            return wrapper
        return decorator

    @__retry_request(max_retries=3, delay=1)
    def __new_multipart_upload(self, dataset_id, zip_index, order_id):
        """
        Start a new multipart upload

        :param str dataset_id Base64 dataset_id
        :param int zip_index Index of zip file
        :param str order_id Base64 order_id

        :returns AWS upload_id
        """
        try:        
            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

            body = {
                'datasetId': dataset_id,
                'zipIndex': str(zip_index),
                'orderId': order_id
            }


            encrypted_body = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/multipartUploadRequest/", data=encrypted_body, headers=headers)

            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            text = res.text
            res_json = self.__decrypt_aes_ctr(text, "json")
            upload_id = res_json["uploadId"]

            return upload_id

        except Exception as e:
            raise Exception(f"Multipart upload initialization failed: {str(e)}")

    @__retry_request(max_retries=3, delay=1)
    def __complete_multipart_upload(self, order_id, dataset_id, zip_index, upload_id, upload_parts):
        """
        Complete a new multipart upload

        :param str order_id Base64 order_id
        :param str dataset_id Base64 dataset_id
        :param int zip_index Index of zip file
        :param str upload_id Base64 upload_id
        :param dict upload_parts Uploaded parts dict

        :returns Status code
        """
        try:
        
            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

            body = {
                'datasetId': dataset_id,
                'zipIndex': zip_index,
                'uploadId': upload_id,
                'uploadParts': upload_parts,
                'orderId': order_id
            }

            encrypted_body = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/completeMultipartUpload/", data=encrypted_body, headers=headers)

            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            return 200

        except Exception as e:
            raise Exception(f"Multipart upload completion failed: {str(e)}")

    @__retry_request(max_retries=3, delay=1)
    def __upload_part(self, upload_id, dataset_id, zip_index, order_id, part_number, part_data):
        """
        Upload a part of the multipart upload

        :param str upload_id Base64 upload_id
        :param str dataset_id Base64 dataset_id
        :param int zip_index Index of zip file
        :param str order_id Base64 orderId
        :param int part_number Part number
        :param bytes part_data Part data

        :return Etag
        """
        try:
            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

            body = {
                'datasetId': dataset_id,
                'uploadId': upload_id,
                'partNumber': str(part_number),
                'zipIndex': str(zip_index),
                'orderId': order_id
            }

            encrypted_body = self.__encrypt_aes_ctr(body, "json", "string")

            # Retrieve a presigned url
            res = requests.post(f"{self.server_url}/api/multipartPresignedUrl/", data=encrypted_body, headers=headers)
            
            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            text = res.text

            res_json = self.__decrypt_aes_ctr(text, "json")
            presigned_url = res_json["presignedUrl"] # URL to upload part

            if(presigned_url is None):
                raise Exception("Presigned URL not present in AWS response.")

            # Put data to presigned url
            res = requests.put(presigned_url, data=part_data)

            if not res.ok:
                raise Exception(res.text)  
                
            e_tag = res.headers.get('ETag')

            if(e_tag is None):
                raise Exception("Etag header not present in AWS response.")

            return e_tag

        except Exception as e:
            raise Exception(f"Upload part failed: {str(e)}")

    # Public Methods

    def get_public_key(self):
        """Retrieve public key from server.

        :param str server_url: Server URL of Neuropacs instance

        :return: Base64 string public key.
        """

        try:

            headers = {'Origin-Type': self.origin_type}

            res = requests.get(f"{self.server_url}/api/getPubKey", headers=headers)

            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            jsn = res.json()
            pub_key = jsn['pub_key']
            return pub_key
        except Exception as e:
            raise Exception(f"Public key retrieval failed: {str(e)}")
            
            
    def connect(self):
        """Create a connection with the server

        Returns:
        :returns: Connection object (timestamp, connection_id, aes_key)
        """

        try:
            headers = {
            'Content-Type': 'text/plain',
            'Origin-Type': self.origin_type,
            'X-Api-Key': self.api_key
            }

            aes_key = self.__generate_aes_key()
            self.aes_key = aes_key

            body = {
                "aes_key": aes_key
            }

            encrypted_body = self.__oaep_encrypt(body)

            res = requests.post(f"{self.server_url}/api/connect/", data=encrypted_body, headers=headers)

            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            jsn = res.json()
            connection_id = jsn["connectionId"]
            self.connection_id = connection_id
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            return {
                "timestamp": formatted_datetime + " UTC",
                "connection_id": connection_id,
                "aes_key": aes_key,
            }
        except Exception as e:
            raise Exception(f"Connection failed: {str(e)}")

    def upload_dataset_from_path(self, order_id=None, path=None, callback=None):
        """Upload a dataset from a file path

        :param str order_id: Unique base64 identifier for the order.
        :param str path: Path to dataset folder to be uploaded (ex. "/path/to/dicom").   
        :param function callback: Callback function invoked with upload progress.

        :return: Boolean indicating upload status.
        """

        try:
            if(order_id is None or path is None):
                raise Exception("Paramter is missing")

            if(self.connection_id is None or self.aes_key is None):
                raise Exception("Missing session parameters, start a new session with 'connect()' and try again.")

            if isinstance(path,str):
                if not os.path.isdir(path):
                    raise Exception("Path not a directory.") 
            else:
                raise Exception("Path must be a string.") 

            # Calculate number of files in the directory
            total_files = 0 
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename) # Get full file path
                    if os.path.isfile(file_path):
                        total_files += 1

            if total_files == 0:
                raise Exception("No files located in path.") 

            part_index = 1 # Counts index of zip file
            files_uploaded = 0 # Track number of files uploaded
            filename_set = set() # Tracks exisitng file names

            # BytesIO object to hold the ZIP file in memory
            zip_buffer = io.BytesIO()

            # Create a write stream into the zip file
            zip_file = zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED)

            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    # Get full file path
                    file_path = os.path.join(dirpath, filename)

                    # Throw error if not a file
                    if not os.path.isfile(file_path):
                        raise Exception(f"Object {file_path} is not a file.")

                    # Generate a unique filename
                    unqiue_filename = self.__ensure_unique_name(filename_set, filename)

                    # Get file contents in bytes
                    file_contents = self.__read_file_contents(file_path)

                    # If next chunk size will be larger than max, start next chunk
                    # next_zip_size = cur_zip_size + file_size
                    if zip_buffer.tell() > self.max_zip_size:                        
                        # Close the zip file
                        zip_file.close()
                        zip_buffer.seek(0)

                        # Get zip file contents in memory
                        zip_file_contents = zip_buffer.getvalue()

                        # Get zip index
                        zip_index = part_index - 1

                        # Start new mulitpart upload
                        upload_id = self.__new_multipart_upload(order_id, str(zip_index), order_id)

                        # Upload part
                        e_tag = self.__upload_part(upload_id, order_id, str(zip_index), order_id, part_index, zip_file_contents)

                        # Complete mulitpart upload
                        self.__complete_multipart_upload(order_id, order_id, str(zip_index), upload_id, [{'PartNumber': part_index, 'ETag': e_tag}])

                        # Clear buffer and reset zip file
                        zip_buffer.seek(0)
                        zip_buffer.truncate(0)
                        zip_file = zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED)

                        # Increment part number
                        part_index += 1
                    
                    # Write file to zip
                    zip_file.writestr(unqiue_filename, file_contents)

                    # Increment files uploaded
                    files_uploaded += 1

                    # Update callback
                    if callback is not None:
                        # Calculate progress and round to two decimal places
                        progress = (files_uploaded / total_files) * 100
                        progress = round(progress, 2)

                        # Ensure progress is exactly 100 if it's effectively 100
                        progress = 100 if progress == 100.0 else progress
                        callback({
                            'order_id': order_id,
                            'progress': progress,
                            'status': f"Uploading file {files_uploaded}/{total_files}"
                        })


            if(zip_buffer.tell() > 0):
                # Upload remaining files in zip_buffer
                
                # Close the zip file
                zip_file.close()
                zip_buffer.seek(0)

                # Get zip file contents in memory
                zip_file_contents = zip_buffer.getvalue()

                # Get zip index
                zip_index = part_index - 1

                # Get upload_id for multipart upload
                upload_id = self.__new_multipart_upload(order_id, str(zip_index), order_id)

                # Upload the zip file
                e_tag = self.__upload_part(upload_id, order_id, str(zip_index), order_id, part_index, zip_file_contents)

                # Complete multipart upload
                self.__complete_multipart_upload(order_id, order_id, str(zip_index), upload_id, [{'PartNumber': part_index, 'ETag': e_tag}])

            # Close the zip file if it's still open
            if zip_file.fp is not None:
                zip_file.close()

            return True

        except Exception as e:
           raise Exception(f"Error uploading dataset from path: {str(e)}")


    def upload_dataset_from_dicom_web(self, order_id=None, wado_url=None, study_uid=None, username=None, password=None, callback=None):
        """
        Upload a dataset via DICOMweb WADO-RS protocol.

        :param str order_id: Unique base64 identifier for the order.
        :param str wado_url: URL to access DICOM images via the WADO-RS protocol (e.g. 'http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/rs').
        :param str study_uid: Unique Study Instance UID of the study to be retrieved.
        :param str username: Username for basic authentication (if required).
        :param str password: Password for basic authentication (if required).
        :param function callback: Callback function invoked with upload progress.

        :return: Boolean indicating upload status.
        """
        try:
            if order_id is None or wado_url is None or study_uid is None:
                raise Exception("Parameter is missing.")

            if(self.connection_id is None or self.aes_key is None):
                raise Exception("Missing session parameters, start a new session with 'connect()' and try again.")

            # Create a DICOMwebClient instance
            try:
                if(username is not None and password is not None):
                    # w/ auth
                    client = DICOMwebClient(
                        url=wado_url,
                        username=username,
                        password=password
                    )
                else:
                    # w/out auth
                    client = DICOMwebClient(
                        url=wado_url
                    )
            except Exception:
                raise ConnectionError("Unable to connect to the DICOMweb server.")


            # Update callback
            if callback is not None:
                callback({
                    'order_id': order_id,
                    'progress': 0,
                    'status': f"Retrieving instances from DICOMweb for study {study_uid}"
                })

            # Retrieve all instances within the study as Datasets
            instances = client.retrieve_study(study_instance_uid=study_uid)

            if instances is None or len(instances) == 0:
                raise Exception(f"No instances recieved from DICOMweb for study {study_uid}")

            # Update callback
            if callback is not None:
                callback({
                    'order_id': order_id,
                    'progress': 100,
                    'status': f"Retrieving instances from DICOMweb for study {study_uid}"
                })

            # BytesIO object to hold the ZIP file in memory
            zip_buffer = io.BytesIO()

            # Create a write stream into the zip file
            zip_file = zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED)

            # Total number of instances
            total_instances = len(instances)

            # Track current part number
            part_number = 1

            # Track total files uploaded
            instances_uploaded = 0

            # Iterate through instances
            for i, instance in enumerate(instances):
                # Serialize the instance to bytes
                buffer = io.BytesIO()
                instance.save_as(buffer)
                data_bytes = buffer.getvalue()
                buffer.close()

                # Generate a unique filename for the current file
                unique_filename = self.__generate_unique_uuid()

                # If max size exceeded OR on last file, upload
                if zip_buffer.tell() > self.max_zip_size:
                    # Close the zip file
                    zip_file.close()
                    zip_buffer.seek(0)

                    # Get zip file contents in memory
                    zip_file_contents = zip_buffer.getvalue()

                    # Get zip index
                    zip_index = part_number - 1

                    # Get upload_id for multipart upload
                    upload_id = self.__new_multipart_upload(order_id, str(zip_index), order_id)

                    # Upload the zip file
                    e_tag = self.__upload_part(upload_id, order_id, str(zip_index), order_id, part_number, zip_file_contents)

                    # Complete multipart upload
                    self.__complete_multipart_upload(order_id, order_id, str(zip_index), upload_id, [{'PartNumber': part_number, 'ETag': e_tag}])

                    # Clear buffer and reset cur_zip_size
                    zip_buffer.seek(0)
                    zip_buffer.truncate(0)
                    zip_file = zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED)

                    # Increment part number
                    part_number += 1

            
                # Add the current instance to the zip
                zip_file.writestr(unique_filename, data_bytes)

                # Incremennt instances uploaded 
                instances_uploaded += 1

                # Update callback
                if callback is not None:
                    # Calculate progress and round to two decimal places
                    progress = (instances_uploaded / total_instances) * 100
                    progress = round(progress, 2)

                    # Ensure progress is exactly 100 if it's effectively 100
                    progress = 100 if progress == 100.0 else progress
                    callback({
                        'order_id': order_id,
                        'progress': progress,
                        'status': f"Uploading instance {instances_uploaded}/{total_instances}"
                    })

            if zip_buffer.tell() > 0:
                # Upload remaining files in zip_buffer
                # Close the zip file
                zip_file.close()
                zip_buffer.seek(0)

                # Get zip file contents in memory
                zip_file_contents = zip_buffer.getvalue()

                # Get zip index
                zip_index = part_number - 1

                # Get upload_id for multipart upload
                upload_id = self.__new_multipart_upload(order_id, str(zip_index), order_id)

                # Upload the zip file
                e_tag = self.__upload_part(upload_id, order_id, str(zip_index), order_id, part_number, zip_file_contents)

                # Complete multipart upload
                self.__complete_multipart_upload(order_id, order_id, str(zip_index), upload_id, [{'PartNumber': part_number, 'ETag': e_tag}])

            # Close the zip file if it's still open
            if zip_file.fp is not None:
                zip_file.close()

            return True

        except Exception as e:
            raise Exception(f"Error uploading dataset from DICOMweb: {str(e)}")

    def new_job (self):
        """Create a new order

        :return: Unique base64 identifier for the order.
        """
        try:
            if(self.connection_id is None or self.aes_key is None):
                raise Exception("Missing session parameters, start a new session with 'connect()' and try again.")

            headers = {'Content-type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

            res = requests.get(f"{self.server_url}/api/newJob/", headers=headers)

            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            text = res.text
            decrypted_text = self.__decrypt_aes_ctr(text, "string")

            order_id = json.loads(decrypted_text)["orderId"]

            self.order_id = order_id
            return order_id
        except Exception as e:
            raise Exception(f"Job creation failed: {str(e)}")
           
    def run_job(self, order_id=None, product_name=None):
        """Run a job
        
        :prarm str order_id: Unique base64 identifier for the order.
        :param str product_name: Product to be executed.
        
        
        :return: Job run status code.
        """

        try:
            if order_id == None or product_name is None:
                raise Exception("Parameter is missing")
    
            if(self.connection_id is None or self.aes_key is None):
                raise Exception("Missing session parameters, start a new session with 'connect()' and try again.")

            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

            body = {
                'orderId': order_id,
                'productName': product_name,
            }

            encryptedBody = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/runJob/", data=encryptedBody, headers=headers)
            
            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            return res.status_code
                
        except Exception as e:
            raise Exception(f"Job run failed: {str(e)}")
  
    def check_status(self, order_id=None):
        """Check job status for a specified order

        :param str order_id: Unique base64 identifier for the order.

        :return: Job status message in JSON.
        """
        try:
            if order_id is None:
                raise Exception("Parameter is missing")

            if(self.connection_id is None or self.aes_key is None):
                raise Exception("Missing session parameters, start a new session with 'connect()' and try again.")

            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

        
            body = {
                'orderId': order_id,
            }

            encryptedBody = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/checkStatus/", data=encryptedBody, headers=headers)
            
            if not res.ok:
                raise Exception(json.loads(res.text)["error"])
            
            text = res.text
            jsn = self.__decrypt_aes_ctr(text, "json")
            return jsn
            
        except Exception as e:
            raise Exception(f"Status check failed: {str(e)}")

    def get_results(self, order_id=None, format=None):
        """Get job results for a specified order in a specified format

        :prarm str order_id: Unique base64 identifier for the order.
        :param str format: Format of file data ('txt'/'xml'/'json'/'png')
        
        :return: Result data in specified format
        """
        try:
            if order_id is None or format is None:
                raise Exception("Parameter is missing")

            if(self.connection_id is None or self.aes_key is None):
                raise Exception("Missing session parameters, start a new session with 'connect()' and try again.")

            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

            format = format.lower()

            validFormats = ["txt", "xml", "json", "png"]

            if format not in validFormats:
                raise Exception("Invalid format.")

            body = {
                'orderId': order_id,
                'format': format               
            }

            encrypted_body = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/getResults/", data=encrypted_body, headers=headers)
            
            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            text = res.text

            if format == "txt" or format == "xml" or format == "json":
                return self.__decrypt_aes_ctr(text, "string")
            elif format == "png":
                return self.__decrypt_aes_ctr(text, "bytes")

        except Exception as e:
            raise Exception(f"Result retrieval failed: {str(e)}")