import os
import requests
import json
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64
import zipfile
import io
import uuid
from datetime import datetime
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import requests

class Neuropacs:
    def __init__(self, server_url, api_key, origin_type="API"):
        """
        NeuroPACS constructor
        """
        self.server_url = server_url
        self.api_key = api_key
        self.origin_type = origin_type
        self.connection_id = ""
        self.aes_key = ""
        self.dataset_upload = False
        self.files_uploaded = 0

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
        PUBLIC_KEY = self.get_public_key()

        PUBLIC_KEY = PUBLIC_KEY.encode('utf-8')

        # Deserialize the public key from PEM format
        public_key = serialization.load_pem_public_key(PUBLIC_KEY)

        # Encrypt the plaintext using OAEP padding
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
        :param * format_out: Format of plaintext. Default to "string".

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
        """Generate a random v4 uuid
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

    def __new_multipart_upload(self, dataset_id, zip_index, order_id):
        """
        Start a new multipart upload

        :param str dataset_id Base64 dataset_id
        :param int zip_index Index of zip file
        :param str order_id Base65 order_id

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
            raise Exception(f"ultipart upload completion failed: {str(e)}")

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

            res = requests.post(f"{self.server_url}/api/multipartPresignedUrl/", data=encrypted_body, headers=headers)
            
            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            text = res.text

            res_json = self.__decrypt_aes_ctr(text, "json")
            presigned_url = res_json["presignedUrl"] # URL to upload part

            fail = False
            for attempt in range(3):
                upload_res = requests.put(presigned_url, data=part_data)

                if not upload_res.ok:
                    fail = True
                else:
                    e_tag = upload_res.headers.get('ETag')
                    return e_tag

            if fail:
                raise Exception("Upload failed after 3 attempts")

        except Exception as e:
            raise Exception(f"Upload part failed: {str(e)}")


    def __split_zip_contents(self, zip_contents, part_size):
        """
        Split zip contents into chunk of part_size for upload

        :param bytes zip_contents Bytes content of zip file
        :param int part_size Size of each chunk
        """
        try:
            parts = []
            start = 0
            while start < len(zip_contents):
                end = min(start + part_size, len(zip_contents))
                parts.append(zip_contents[start:end])
                start = end
            return parts
        except Exception as error:
            raise Exception(f"Partitioning blob failed: {str(error)}")

    def __attempt_upload_dataset(self, directory, order_id=None, dataset_id=None, callback=None):
        """Upload a dataset to the server

        :param str directory: Path to dataset folder to be uploaded.
        :param str order_id: Base64 order_id
        :param str dataset_id: Base64 dataset_id
        :param str callback: Function to be called after every upload

        :return: Upload status code.
        """
        try:
            if isinstance(directory,str):
                if not os.path.isdir(directory):
                    raise Exception("Path not a directory") 
            else:
                raise Exception("Path must be a string") 

            if order_id is None:
                order_id = self.order_id

            if dataset_id is None:
                dataset_id = self.__generate_unique_uuid()

            zip_builder_object = {} # Object of chunks, each value is an array of files

            # Calculate number of files in the directory
            total_files = 0 
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename) # Get full file path
                    if os.path.isfile(file_path):
                        total_files += 1

            files_processed = 0

            max_zip_size = 50000000 # Max size of zip file (5MB)
            total_parts = 0 # Counts total parts the dataset is divided into
            cur_zip_size = 0 # Counts size of current zip file
            zip_index = 0 # Counts index of zip file

            file_set = set() # Tracks exisitng file names

            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename) # Get full file path
                    # Throw error if not a file
                    if not os.path.isfile(file_path):
                        raise Exception(f"Object {file_path} is not a file.")

                    cur_zip_size += os.path.getsize(file_path) # Increment current file set size

                    # Create list at zipIndex if it does not already exist
                    if zip_index not in zip_builder_object:
                        zip_builder_object[zip_index] = []
                        total_parts += 1

                    unqiue_filename = self.__ensure_unique_name(file_set, filename)
                
                    # Push file to the list at zipIndex 
                    zip_builder_object[zip_index].append({"filename": unqiue_filename, "path": file_path})

                    # If current chunk size is larger than max, start next chunk
                    if cur_zip_size > max_zip_size:
                        zip_index += 1
                        cur_zip_size = 0

                    files_processed += 1 # Increment number of processed files

                    if callback is not None:
                        # Calculate progress and round to two decimal places
                        progress = (files_processed / total_files) * 100
                        progress = round(progress, 2)

                        # Ensure progress is exactly 100 if it's effectively 100
                        progress = 100 if progress == 100.0 else progress
                        callback({
                            'dataset_id': dataset_id,
                            'progress': progress,
                            'status': "Preprocessing"
                        })

            # Start zipping and uploading each chunk
            for chunk in zip_builder_object:
                # Get upload_id for this chunk
                upload_id = self.__new_multipart_upload(dataset_id, chunk, order_id)

                # BytesIO object to hold the ZIP file in memory
                zip_buffer = io.BytesIO()

                # Create a write stream into the zip file
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    cur_chunk = zip_builder_object[chunk]
                    # For each file in the chunk, add to zip buffer
                    for file in range(len(cur_chunk)):
                        filename = cur_chunk[file]['filename']
                        path = cur_chunk[file]['path']
                        file_contents = self.__read_file_contents(path)
                        zip_file.writestr(filename, file_contents)
                        # Call progress callback
                        if callback is not None:
                            # Calculate progress and round to two decimal places
                            progress = ((file+1) / len(cur_chunk)) * 100
                            total_progress = round(
                                (100 / (2 * total_parts)) *
                                (2 * (chunk + 1 - 1) + progress / 100)
                                ,2)
                            callback({
                                'dataset_id': dataset_id,
                                'progress': total_progress,
                                'status': f"Compressing part {chunk+1}/{total_parts}"
                            })

                # Seek to the beginning of the BytesIO object before reading
                zip_buffer.seek(0)

                # Get zip file contents in memory
                zip_file_contents = zip_buffer.getvalue()

                part_size = 5 * 1024 * 1024 # 5MB minimum part size

                # Break zip contents into chunks of part_size
                zip_parts = self.__split_zip_contents(zip_file_contents, part_size)

                final_parts = [] # Holds part details for complete multi upload

                for up in range(len(zip_parts)):
                    e_tag = self.__upload_part(upload_id, dataset_id, chunk, order_id, up+1, zip_parts[up])

                    final_parts.append({'PartNumber': up+1, 'ETag': e_tag})

                    # Call progress callback
                    if callback is not None:
                        # Calculate progress and round to two decimal places
                        progress = ((up+1) / len(zip_parts)) * 100
                        total_progress = round(
                            (100 / (2 * total_parts)) *
                            (2 * (chunk + 1 - 1) + 1 + progress / 100)
                            ,2)

                        # Ensure progress is exactly 100 if it's effectively 100
                        total_progress = 100 if total_progress == 100.0 else total_progress
                        callback({
                            'dataset_id': dataset_id,
                            'progress': total_progress,
                            'status': f"Uploading part {chunk+1}/{total_parts}"
                        })

                self.__complete_multipart_upload(order_id, dataset_id, str(chunk), upload_id, final_parts)

            return dataset_id

        except Exception as e:
           raise Exception(f"Dataset upload failed: {str(e)}")

    def __split_array(self, array, part_size):
        """
        Split array into part_size pieces for processing.
        
        :param str array List to be split
        :param int part_size Size of each chunk

        :return: List of chunks
        """
        if part_size <= 0:
            raise ValueError("Chunk size must be greater than 0")

        result = []
        for i in range(0, len(array), part_size):
            chunk = array[i:i + part_size]
            result.append(chunk)
        return result

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
        :returns: Connection object (timestamp, connection_id, order_id)
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
            raise Exception(f"Connection creation failed: {str(e)}")
            


    def upload_dataset(self, directory, order_id=None, dataset_id=None, callback=None):
        """Upload a dataset to the server

        :param str directory: Path to dataset folder to be uploaded.
        :param str order_id: Base64 order_id
        :param str dataset_id: Base64 dataset_id
        :param str callback: Function to be called after every upload

        :return: Upload status code.
        """
        try:
            # Attempt upload
            dataset_id_complete = self.__attempt_upload_dataset(directory, order_id, dataset_id, callback)
            # Return result
            return { "dataset_id": dataset_id_complete, "state": "success" }
        except Exception as e:
            raise Exception(f"Dataset upload failed: {str(e)}")


    def validate_upload(self, directory, dataset_id, order_id=None, callback=None):
        """
        Validate dataset upload

        :param list directory Path to dataset
        :param str dataset_id Base64 dataset_id
        :param str order_id Base64 order_id

        :returns List of missing files
        """
        try:
            if order_id is None:
                order_id = self.order_id

            file_list = [] # Holds list of files (filename, size)

            total_file_count = 0 # Tracks total number of files in dataset

            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename) # Get full file path
                    size = os.path.getsize(file_path)
                    file_list.append({'name': filename, 'size': size})
                    total_file_count +=1

            validation_parts = self.__split_array(file_list, 100)

            encrypted_order_id = self.__encrypt_aes_ctr(order_id, "string", "string")
        
            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

            total_validated = 0 # Total files validated

            total_missing_files = [] # Store list of missing files

            for val in range(len(validation_parts)):
                body = {
                    'fileMetadata': validation_parts[val],
                    'orderId': order_id,
                    'datasetId': dataset_id
                }

                encrypted_body = self.__encrypt_aes_ctr(body, "json", "string")

                res = requests.post(f"{self.server_url}/api/verifyUpload/", data=encrypted_body, headers=headers)
            
                if not res.ok:
                    raise Exception(json.loads(res.text)["error"])

                text = res.text
                decrypted_dataset_validation = self.__decrypt_aes_ctr(text, "json")
                total_missing_files = total_missing_files + decrypted_dataset_validation['missingFiles']
                total_validated += len(validation_parts[val])

                if callback is not None:
                    # Calculate progress and round to two decimal places
                    progress = (total_validated / total_file_count) * 100
                    progress = round(progress, 2)

                    # Ensure progress is exactly 100 if it's effectively 100
                    progress = 100 if progress == 100.0 else progress
                    callback({
                        'dataset_id': dataset_id,
                        'progress': progress,
                        'status': "Validating"
                    })

            return {'missingFiles': total_missing_files}

        except Exception as e:
            raise Exception(f"Upload validation failed: {str(e)}")


    def new_job (self):
        """Create a new order

        :return: Base64 string order_id.
        """
        try:
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
           


    def run_job(self, product_name, order_id=None):
        """Run a job
        
        :param str product_name: Product to be executed.
        :prarm str order_id: Base64 order_id 
        :prarm str dataset_id: Base64 dataset_id 
        
        :return: Job run status code.
        """

        try:

            if order_id == None:
                order_id = self.order_id

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
        """Check job status

        :param str order_id: Base64 order_id (optional)
        :param str dataset_id: Base64 dataset_id (optional)

        :return: Job status message.
        """
        if order_id is None:
            order_id = self.order_id

        try:

            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

        
            body = {
                'orderId': order_id,
            }

            encryptedBody = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/checkStatus/", data=encryptedBody, headers=headers)
            
            if not res.ok:
                raise Exception(json.loads(res.text)["error"])
            
            text = res.text
            json = self.__decrypt_aes_ctr(text, "json")
            return json
            
        except Exception as e:
            raise Exception(f"Status check failed: {str(e)}")
 


    def get_results(self, format, order_id=None):
        """Get job results

        :param str format: Format of file data
        :prarm str order_id: Base64 order_id (optional)
        :param str dataset_id: Base64 dataset_id

        :return: AES encrypted file data in specified format
        """
        try:
            if order_id is None:
                order_id = self.order_id

            headers = {'Content-Type': 'text/plain', 'Connection-Id': self.connection_id, 'Origin-Type': self.origin_type}

            body = {
                'orderId': order_id,
                'format': format               
            }

            validFormats = ["TXT", "XML", "JSON", "PNG"]

            if format not in validFormats:
                raise Exception("Invalid format! Valid formats include: \"TXT\", \"JSON\", \"XML\", \"PNG\".")

            encrypted_body = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/getResults/", data=encrypted_body, headers=headers)
            
            if not res.ok:
                raise Exception(json.loads(res.text)["error"])

            text = res.text

            if format == "TXT" or format == "XML" or format == "JSON":
                return self.__decrypt_aes_ctr(text, "string")
            elif format == "PNG":
                return self.__decrypt_aes_ctr(text, "bytes")

        except Exception as e:
            raise Exception(f"Result retrieval failed: {str(e)}")



    