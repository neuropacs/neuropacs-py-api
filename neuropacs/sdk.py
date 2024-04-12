import os
import requests
import json
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64
import string
import secrets
from datetime import datetime
from tqdm import tqdm
import hashlib
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import requests

class Neuropacs:
    def __init__(self, server_url, api_key, client="api"):
        """
        NeuroPACS constructor
        """
        self.server_url = server_url
        self.api_key = api_key
        self.client = client
        self.aes_key = self.__generate_aes_key()
        self.connection_id = ""
        self.aes_key = ""
        self.dataset_upload = False
        self.files_uploaded = 0

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

            decrypted_data = decrypted.decode("utf-8")

            if format_out == "json":
                decrypted_data = json.loads(decrypted_data)
            elif format_out == "string":
                pass

            return decrypted_data
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError']) 
            else:
                raise Exception("AES decryption failed!")
    
    def __generate_filename(self):
        """Generate a filename for byte data
        :return: 20 character random alphanumeric string
        """
        characters = string.ascii_letters + string.digits
        random_string = ''.join(secrets.choice(characters) for _ in range(20))
        return random_string

    def get_public_key(self, server_url=None):
        """Retrieve public key from server.

        :param str server_url: Server URL of Neuropacs instance

        :return: Base64 string public key.
        """

        if server_url is None:
            server_url = self.server_url

        try:
            res = requests.get(f"{server_url}/api/getPubKey")

            if not res.ok:
                raise Exception({"neuropacsError": f"{res.text}"})

            json = res.json()
            pub_key = json['pub_key']
            return pub_key
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError']) 
            else:
                raise Exception("Public key retrieval failed.")
            
            
    def connect(self):
        """Create a connection with the server

        :param str client: Client source (default = 'api')

        Returns:
        :returns: Connection object (timestamp, connection_id, order_id)
        """

        try:
            headers = {
            'Content-Type': 'text/plain',
            'client': self.client
            }

            aes_key = self.__generate_aes_key()
            self.aes_key = aes_key

            body = {
                "aes_key": aes_key,
                "api_key": self.api_key
            }

            encrypted_body = self.__oaep_encrypt(body)

            res = requests.post(f"{self.server_url}/api/connect/", data=encrypted_body, headers=headers)

            if not res.ok:
                raise Exception({"neuropacsError": f"{res.text}"})

            json = res.json()
            connection_id = json["connectionID"]
            self.connection_id = connection_id
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            return {
                "timestamp": formatted_datetime + " UTC",
                "connection_id": connection_id,
                "aes_key": aes_key,
            }
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError']) 
            else:
                raise Exception("Connection failed.")
            


    def upload_dataset(self, directory, order_id=None, connection_id=None, callback=None):
        """Upload a dataset to the server

        :param str directory: Path to dataset folder to be uploaded.
        :param str order_id: Base64 order_id
        :param str connection_id: Base64 connection_id
        :param str callback: Function to be called after every upload

        :return: Upload status code.
        """
        if order_id is None:
            order_id = self.order_id

        if connection_id is None:
            connection_id = self.connection_id

        try:
            self.dataset_upload = True
            
            if isinstance(directory,str):
                if not os.path.isdir(directory):
                    raise Exception({"neuropacsError": "Path not a directory!"}) 
            else:
                raise Exception({"neuropacsError": "Path must be a string!"}) 

            dataset_id = self.__generate_filename()

            total_files = sum(len(filenames) for _, _, filenames in os.walk(directory))

            files_uploaded = 0

            with tqdm(total=total_files, desc="Uploading", unit="file") as prog_bar:
                for dirpath, _, filenames in os.walk(directory):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        status = self.upload(file_path, dataset_id, order_id, connection_id)
                        if status != 201:
                            if callback is not None:
                               callback({
                                'datasetId': dataset_id,
                                'progress': -1,
                                }) 
                            raise Exception({"neuropacsError": "Upload failed!"})
                        files_uploaded += 1
                        if callback is not None:
                            # Calculate progress and round to two decimal places
                            progress = (files_uploaded / total_files) * 100
                            progress = round(progress, 2)

                            # Ensure progress is exactly 100 if it's effectively 100
                            progress = 100 if progress == 100.0 else progress
                            callback({
                                'datasetId': dataset_id,
                                'progress': progress,
                                'filesUploaded': files_uploaded
                            })
                        
                        prog_bar.update(1)  # Update the outer progress bar for each file
            
            return dataset_id

        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError']) 
            else:
                raise Exception("Dataset upload failed.")


    def upload(self, data, dataset_id, order_id=None, connection_id=None):
        """Upload a file to the server

        :param str/bytes data: Path of file to be uploaded or byte array
        :param str dataset_id Base64 dataset_id
        :param str order_id: Base64 order_id 
        :param str connection_id: Base64 connection_id

        :return: Upload status code.
        """

        # if not self.dataset_upload:

        if order_id is None:
            order_id = self.order_id

        if connection_id is None:
            connection_id = self.connection_id

        # get file name
        filename = ""
        if isinstance(data,bytes):
            filename = self.__generate_filename()
        elif isinstance(data,str):
            if os.path.isfile(data):
                normalized_path = os.path.normpath(data)
                directories = normalized_path.split(os.sep)
                filename = directories[-1]
            else:
                raise Exception({"neuropacsError": "Path not a file!"})
        else:
            raise Exception({"neuropacsError": "Unsupported data type!"})

        # encrypt order ID
        encrypted_order_id = self.__encrypt_aes_ctr(order_id, "string", "string")

        # create headers
        headers = {"Content-Type": "application/octet-stream",'connection-id': connection_id, 'client': self.client, 'order-id': encrypted_order_id, 'filename': filename, 'dataset-id': dataset_id}

        # get s3 upload params
        res = requests.get(f"{self.server_url}/api/uploadRequest/", headers=headers)

        if not res.ok:
            raise Exception({"neuropacsError": f"{res.text}"})

        decrypted_s3_info = self.__decrypt_aes_ctr(res.text, "json")

        presigned_url = decrypted_s3_info["presignedURL"]

        form = {
            "Content-Disposition": "form-data",
            "filename": filename,
            "name":"test123"
        }

        BOUNDARY = "neuropacs----------"
        DELIM = ";"
        CRLF = "\r\n"
        SEPARATOR="--"+BOUNDARY+CRLF
        END="--"+BOUNDARY+"--"+CRLF
        CONTENT_TYPE = "Content-Type: application/octet-stream"

        header = SEPARATOR
        for key, value in form.items():
            header += f"{key}: {value}"
            header += DELIM
        header += CRLF
        header += CONTENT_TYPE
        header += CRLF + CRLF

        header_bytes = header.encode("utf-8")

        footer_bytes = END.encode("utf-8")

        encrypted_order_id = self.__encrypt_aes_ctr(order_id, "string", "string")

        payload_data = None

        if isinstance(data, bytes):
            # encrypted_binary_data = self.__encrypt_aes_ctr(data, "bytes","bytes")
            payload_data = header_bytes + data + footer_bytes
        
        elif isinstance(data,str):
            with open(data, 'rb') as f:
                binary_data = f.read()
                # encrypted_binary_data = self.__encrypt_aes_ctr(binary_data, "bytes","bytes")
                payload_data = header_bytes + binary_data + footer_bytes


        res = requests.put(presigned_url, data=payload_data)

        if not res.ok:
            raise Exception({"neuropacsError": f"{res.text}"})

        return 201

    def validate_upload(self, file_array, dataset_id, order_id=None, connection_id=None):
        """
        Validate dataset upload
        """
        if connection_id is None:
            connection_id = self.connection_id
        if order_id is None:
            order_id = self.order_id
        try:
            encrypted_order_id = self.__encrypt_aes_ctr(order_id, "string", "string")
        
            headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'dataset-id': dataset_id,'order-id': encrypted_order_id, 'client': self.client}

            body = {
                'fileArray': file_array,
            }

            encrypted_body = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/verifyUpload/", data=encrypted_body, headers=headers)
            
            if not res.ok:
                raise Exception({"neuropacsError": f"{res.text}"})

            text = res.text
            decrypted_dataset_validation = self.__decrypt_aes_ctr(text, "string")
            return decrypted_dataset_validation

        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError'])
            else:
                raise Exception(f"Result retrieval failed!")
        



    def new_job (self, connection_id=None):
        """Create a new order

        :param str connection_id: Base64 connection_id

        :return: Base64 string order_id.
        """

        if connection_id is None:
            connection_id = self.connection_id

        try:
            headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'client': self.client}

            res = requests.post(f"{self.server_url}/api/newJob/", headers=headers)

            if not res.ok:
                raise Exception({"neuropacsError": f"{res.text}"})

            text = res.text
            decrypted_text = self.__decrypt_aes_ctr(text, "string")
            self.order_id = decrypted_text
            return decrypted_text
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError'])
            else:
                raise Exception("Job creation failed.")            


    def run_job(self, product_id, order_id=None, dataset_id=None, connection_id=None):
        """Run a job
        
        :param str productID: Product to be executed.
        :prarm str order_id: Base64 order_id 
        :prarm str dataset_id: Base64 dataset_id 
        :param str connection_id: Base64 connection_id
        
        :return: Job run status code.
        """
        if order_id == None:
            order_id = self.order_id

        if connection_id is None:
            connection_id = self.connection_id

        try:
            headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'client': self.client}

            body={}
            if dataset_id is None:
                body = {
                    'orderID': order_id,
                    'productID': product_id,
                }
            else:
                body = {
                    'orderID': order_id,
                    'productID': product_id,
                    'datasetID': dataset_id
                }

            encryptedBody = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/runJob/", data=encryptedBody, headers=headers)
            
            if not res.ok:
                raise Exception({"neuropacsError": f"{res.text}"})

            return res.status_code
                
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError'])
            else:
                raise Exception("Job run failed.")  


    def check_status(self, order_id=None, dataset_id=None, connection_id=None):
        """Check job status

        :param str order_id: Base64 order_id (optional)
        :param str dataset_id: Base64 dataset_id (optional)
        :param str connection_id: Base64 connection_id

        :return: Job status message.
        """
        if order_id is None:
            order_id = self.order_id

        if connection_id is None:
            connection_id = self.connection_id

        try:

            headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'client': self.client}

            if dataset_id is not None:
                body = {
                    'orderID': order_id,
                    'datasetID': dataset_id
                }
            else:
               body = {
                    'orderID': order_id,
                }

            encryptedBody = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/checkStatus/", data=encryptedBody, headers=headers)
            
            if not res.ok:
                raise Exception({"neuropacsError": f"{res.text}"})
            
            text = res.text
            json = self.__decrypt_aes_ctr(text, "json")
            return json
            
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError'])
            else:
                raise Exception("Status check failed.")  


    def get_results(self, format, order_id=None, dataset_id=None, connection_id=None):
        """Get job results

        :param str format: Format of file data
        :prarm str order_id: Base64 order_id (optional)
        :param str connection_id: Base64 connection_id

        :return: AES encrypted file data in specified format
        """

        if order_id is None:
            order_id = self.order_id

        if connection_id is None:
            connection_id = self.connection_id
        
        try:
        
            headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'client': self.client}

            if dataset_id is not None:
                body = {
                    'orderID': order_id,
                    'format': format,
                    'datasetID': dataset_id
                }
            else:
                body = {
                    'orderID': order_id,
                    'format': format               
                }

            validFormats = ["TXT", "XML", "JSON", "PDF", "DCM"]

            if format not in validFormats:
                raise Exception({"neuropacsError" : "Invalid format! Valid formats include: \"TXT\", \"JSON\", \"XML\", \"PDF\", \"DCM\" ."})

            encrypted_body = self.__encrypt_aes_ctr(body, "json", "string")

            res = requests.post(f"{self.server_url}/api/getResults/", data=encrypted_body, headers=headers)
            
            if not res.ok:
                raise Exception({"neuropacsError": f"{res.text}"})

            text = res.text
            decrypted_file_data = self.__decrypt_aes_ctr(text, "string")
            return decrypted_file_data

        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise Exception(e.args[0]['neuropacsError'])
            else:
                raise Exception(f"Result retrieval failed!")


    