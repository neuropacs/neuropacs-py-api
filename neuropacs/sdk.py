import os
import requests
import json
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64
import string
import secrets
from datetime import datetime
import time
from tqdm import tqdm
import socketio
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
        self.sio = socketio.Client()
        self.__setup_socket_events()
        self.ack_recieved = False
        self.dataset_upload = False
        self.files_uploaded = 0


    def __setup_socket_events(self):
        # self.sio.on('connect', self.on_socket_connect)
        self.sio.on('ack', self.__on_socket_ack)
        # self.sio.on('disconnect', self.on_socket_disconnect)

    # @staticmethod
    # def __on_socket_connect(self):
    #     print('Upload socket connected.')

    # @staticmethod
    # def __on_socket_disconnect(self):
    #     print('Upload socket disconnected.')

    def __on_socket_ack(self, data):
        if data == "0":
            self.ack_recieved = True
            self.files_uploaded += 1
        else:
            self.__disconnect_from_socket()
            raise Exception({"neuropacsError": "Upload failed on server side, ending upload process."})    
            
    def __disconnect_from_socket(self):
        self.sio.disconnect()

    def __connect_to_socket(self):
        self.ack_recieved = False
        self.sio.connect(self.server_url, transports='websocket')

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
                raise e.args[0]['neuropacsError'] 
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
                raise e.args[0]['neuropacsError'] 
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

            if format_out == "JSON":
                decrypted_data = json.loads(decrypted_data)
            elif format_out == "string":
                pass

            return decrypted_data
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise e.args[0]['neuropacsError'] 
            else:
                raise Exception("AES decryption failed!")
    
    def __generate_filename(self):
        """Generate a filename for byte data
        :return: 20 character random alphanumeric string
        """
        characters = string.ascii_letters + string.digits
        random_string = ''.join(secrets.choice(characters) for _ in range(20))
        return random_string

    def get_public_key(self):
        """Retrieve public key from server.

        :return: Base64 string public key.
        """
        try:
            res = requests.get(f"{self.server_url}/api/getPubKey")

            if not res.ok:
                raise Exception({"neuropacsError": f"{res.text}"})

            json = res.json()
            pub_key = json['pub_key']
            return pub_key
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise e.args[0]['neuropacsError'] 
            else:
                raise Exception("Public key retrieval failed.")
            
            
    def connect(self):
        """Create a connection with the server

        Returns:
        :returns: Connection object (timestamp, connection_id, order_id)
        """
        try:
            headers = {
            'Content-Type': 'text/plain',
            'client': self.client
            }

            self.aes_key = self.__generate_aes_key()

            body = {
                "aes_key": self.aes_key,
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
                "aes_key": self.aes_key,
            }
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise e.args[0]['neuropacsError'] 
            else:
                raise Exception("Connection failed.")
            


    def upload_dataset(self, directory, order_id=None):
        """Upload a dataset to the server

        :param str directory: Path to dataset folder to be uploaded.
        :param str order_id: Base64 order_id (optional)

        :return: Upload status code.
        """
        try:
    
            if order_id == None:
                order_id = self.order_id

            self.dataset_upload = True
            self.__connect_to_socket()

            if isinstance(directory,str):
                if not os.path.isdir(directory):
                    raise Exception({"neuropacsError": "Path not a directory!"}) 
            else:
                raise Exception({"neuropacsError": "Path must be a string!"}) 

            total_files = sum(len(filenames) for _, _, filenames in os.walk(directory))

            with tqdm(total=total_files, desc="Uploading", unit="file") as prog_bar:
                for dirpath, _, filenames in os.walk(directory):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        self.upload(file_path, order_id)
                        prog_bar.update(1)  # Update the outer progress bar for each file
    
            self.__disconnect_from_socket()
            return 201  
        except Exception as e:
            if(isinstance(e.args[0], dict) and 'neuropacsError' in e.args[0]):
                raise e.args[0]['neuropacsError'] 
            else:
                raise Exception("Dataset upload failed.")


    def upload(self, data, order_id=None):
        """Upload a file to the server

        :param str/bytes data: Path of file to be uploaded or byte array
        :param str order_id: Base64 order_id (optional)

        :return: Upload status code.
        """

        if order_id == None:
            order_id = self.order_id

        self.ack_recieved = False

        if not self.dataset_upload:
            self.__connect_to_socket()

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

        encrypted_order_id = self.__encrypt_aes_ctr(order_id, "string", "string")

        if isinstance(data,bytes):
            encrypted_binary_data = self.__encrypt_aes_ctr(data, "bytes","bytes")

            message = header_bytes + encrypted_binary_data + END.encode("utf-8")

            headers = {
            "Content-Type": "application/octet-stream",'connection-id': self.connection_id, 'client': self.client, 'order-id': encrypted_order_id
            }

            self.sio.emit('file_data', {'data': message, 'headers': headers})

            max_ack_wait_time = 10   #10 seconds
            start_time = time.time()
            elapsed_time = 0
            while (not self.ack_recieved) and (elapsed_time < max_ack_wait_time):
                elapsed_time = time.time() - start_time

            if elapsed_time > max_ack_wait_time:
                self.__disconnect_from_socket()
                raise Exception({"neuropacsError" : f"Upload timeout!"})

            if not self.dataset_upload:
                self.__disconnect_from_socket()

            return 201
                
        elif isinstance(data,str):
            with open(data, 'rb') as f:
                binary_data = f.read()

                encrypted_binary_data = self.__encrypt_aes_ctr(binary_data, "bytes","bytes")

                message = header_bytes + encrypted_binary_data + END.encode("utf-8")

                headers = {
                "Content-Type": "application/octet-stream",'connection-id': self.connection_id, 'client': self.client, 'order-id': encrypted_order_id
                }

                self.sio.emit('file_data', {'data': message, 'headers': headers})

                max_ack_wait_time = 10   #10 seconds

                start_time = time.time()
                elapsed_time = 0
                while (not self.ack_recieved) and (elapsed_time < max_ack_wait_time):
                    elapsed_time = time.time() - start_time

                if elapsed_time > max_ack_wait_time:
                    self.__disconnect_from_socket()
                    raise Exception({"neuropacsError": f"Upload timeout!"})

                if not self.dataset_upload:
                    self.__disconnect_from_socket()

                return 201


    def new_job (self):
        """Create a new order

        :return: Base64 string order_id.
        """
        try:
            headers = {'Content-type': 'text/plain', 'connection-id': self.connection_id, 'client': self.client}

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


    def run_job(self, product_id, order_id=None):
        """Run a job
        
        :param str productID: Product to be executed.
        :prarm str order_id: Base64 order_id (optional)
        
        :return: Job run status code.
        """
        try:
            if order_id == None:
                order_id = self.order_id

            headers = {'Content-type': 'text/plain', 'connection-id': self.connection_id, 'client': self.client}

            body = {
                'orderID': order_id,
                'productID': product_id
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


    def check_status(self, order_id=None, dataset_id=None):
        """Check job status

        :param str order_id: Base64 order_id (optional)
        :param str dataset_id: Base64 dataset_id (optional)
        
        :return: Job status message.
        """

        try:
            if order_id == None:
                order_id = self.order_id

            headers = {'Content-type': 'text/plain', 'connection-id': self.connection_id, 'client': self.client}

            body = {
                'orderID': order_id,
                'datasetID': dataset_id
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
            


    def get_results(self, format, order_id=None, dataset_id=None):
        """Get job results

        :param str format: Format of file data
        :prarm str order_id: Base64 order_id (optional)

        :return: AES encrypted file data in specified format
        """
        try:
            if order_id == None:
                order_id = self.order_id

            headers = {'Content-type': 'text/plain', 'connection-id': self.connection_id, 'client': self.client}

            body = {
                'orderID': order_id,
                'format': format,
                'datasetID': dataset_id
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


    