import os
import requests
import json
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
import base64
import string
import secrets
import time
from tqdm import tqdm
import socketio
from Crypto.Cipher import AES, PKCS1_v1_5
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import requests
import base64

class Neuropacs:
    def __init__(self, server_url):
        """
        NeuroPACS constructor
        """
        self.server_url = server_url
        self.sio = socketio.Client()
        self.setup_socket_events()
        self.ack_recieved = False
        self.dataset_upload = False
        self.files_uploaded = 0

    def setup_socket_events(self):
        # self.sio.on('connect', self.on_socket_connect)
        self.sio.on('ack', self.on_socket_ack)
        # self.sio.on('disconnect', self.on_socket_disconnect)

    # def on_socket_connect(self):
    #     print('Upload socket connected.')

    # def on_socket_disconnect(self):
    #     print('Upload socket disconnected.')

    def on_socket_ack(self, data):
        if data == "0":
            self.ack_recieved = True
            self.files_uploaded += 1
        else:
            print("Upload failed on server side, ending upload process.")
            self.disconnect_from_socket()
        
    def disconnect_from_socket(self):
        self.sio.disconnect()

    def connect_to_socket(self):
        self.ack_recieved = False
        self.sio.connect(self.server_url, transports='websocket')

    def generate_aes_key(self):
        """Generate an 16-byte AES key for AES-CTR encryption.

        :return: AES key encoded as a base64 string.
        """
        aes_key = get_random_bytes(16)
        aes_key_base64 = base64.b64encode(aes_key).decode('utf-8')
        return aes_key_base64

    def oaep_encrypt(self, plaintext):
        """
        OAEP encrypt plaintext.

        :param str/JSON plaintext: Plaintext to be encrypted.

        :return: Base64 string OAEP encrypted ciphertext
        """

        try:
            plaintext = json.dumps(plaintext)
        except:
            if not isinstance(plaintext, str):
                raise Exception("Plaintext must be a string or JSON!")    

    
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

    def connect(self, api_key, aes_key):
        """Create a connection with the server

        :param str api_key: Base64 API key.
        :param str aes_key: Base64 AES key.

        Returns:
        :returns: Base64 string encrypted AES key.
        """

    
        headers = {
        'Content-Type': 'text/plain',
        'client': 'api'
        }

        body = {
            "aes_key": aes_key,
            "api_key": api_key
        }

        encrypted_body = self.oaep_encrypt(body)

        res = requests.post(f"{self.server_url}/connect/", data=encrypted_body, headers=headers)

        if res.status_code == 200:
                json = res.json()
                connection_id = json["connectionID"]
                return connection_id
        else:
            raise Exception(f"Connection failed!")

    def get_public_key(self):
        """Retrieve public key from server.

        :return: Base64 string public key.
        """
        res = requests.get(f"{self.server_url}/getPubKey")
        if(res.status_code != 200):
            raise Exception(f"Public key retrieval failed!")
            

        json = res.json()
        pub_key = json['pub_key']
        return pub_key


    def upload_dataset(self, directory, order_id, connection_id, aes_key):
        """Upload a dataset to the server

        :param str directory: Path to dataset folder to be uploaded.
        :param str order_id: Base64 order_id.
        :param str connection_id: Base64 connection_id.
        :param str aes_key: Base64 AES key.

        :return: Upload status code.
        """
        self.dataset_upload = True
        self.connect_to_socket()

        if isinstance(directory,str):
            if not os.path.isdir(directory):
                raise Exception("Path not a directory!") 
        else:
            raise Exception("Path must be a string!") 

        total_files = sum(len(filenames) for _, _, filenames in os.walk(directory))

        with tqdm(total=total_files, desc="Uploading", unit="file") as prog_bar:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    self.upload(file_path, order_id, connection_id, aes_key)
                    prog_bar.update(1)  # Update the outer progress bar for each file
 
        self.disconnect_from_socket()
        return 201   

    def upload(self, data, order_id, connection_id, aes_key):
        """Upload a file to the server

        :param str/bytes data: Path of file to be uploaded or byte array
        :param str order_id: Base64 order_id.
        :param str connection_id: Base64 connection_id.
        :param str aes_key: Base64 AES key.

        :return: Upload status code.
        """
        self.ack_recieved = False

        if not self.dataset_upload:
            self.connect_to_socket()

        filename = ""

        if isinstance(data,bytes):
            filename = self.generate_filename()
        elif isinstance(data,str):
            if os.path.isfile(data):
                normalized_path = os.path.normpath(data)
                directories = normalized_path.split(os.sep)
                filename = directories[-1]
            else:
                raise Exception("Path not a file!")
        else:
            raise Exception("Unsupported data type!")

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

        encrypted_order_id = self.encrypt_aes_ctr(order_id, aes_key, "string", "string")

        if isinstance(data,bytes):
            encrypted_binary_data = self.encrypt_aes_ctr(data, aes_key, "bytes","bytes")

            message = header_bytes + encrypted_binary_data + END.encode("utf-8")

            headers = {
            "Content-Type": "application/octet-stream",'connection-id': connection_id, 'client': 'API', 'order-id': encrypted_order_id
            }

            self.sio.emit('file_data', {'data': message, 'headers': headers})

            max_ack_wait_time = 10   #10 seconds
            start_time = time.time()
            elapsed_time = 0
            while (not self.ack_recieved) and (elapsed_time < max_ack_wait_time):
                elapsed_time = time.time() - start_time

            if elapsed_time > max_ack_wait_time:
                self.disconnect_from_socket()
                raise Exception(f"Upload timeout!")

            if not self.dataset_upload:
                self.disconnect_from_socket()

            return 201
                
        elif isinstance(data,str):
            with open(data, 'rb') as f:
                binary_data = f.read()

                encrypted_binary_data = self.encrypt_aes_ctr(binary_data,aes_key,"bytes","bytes")

                message = header_bytes + encrypted_binary_data + END.encode("utf-8")

                headers = {
                "Content-Type": "application/octet-stream",'connection-id': connection_id, 'client': 'API', 'order-id': encrypted_order_id
                }

                self.sio.emit('file_data', {'data': message, 'headers': headers})

                max_ack_wait_time = 10   #10 seconds

                start_time = time.time()
                elapsed_time = 0
                while (not self.ack_recieved) and (elapsed_time < max_ack_wait_time):
                    elapsed_time = time.time() - start_time

                if elapsed_time > max_ack_wait_time:
                    self.disconnect_from_socket()
                    raise Exception(f"Upload timeout!")

                if not self.dataset_upload:
                    self.disconnect_from_socket()

                return 201

    def generate_filename(self):
        """Generate a filename for byte data
        :return: 20 character random alphanumeric string
        """
        characters = string.ascii_letters + string.digits
        random_string = ''.join(secrets.choice(characters) for _ in range(20))
        return random_string

    def new_job (self, connection_id, aes_key):
        """Create a new order

        :param str connection_id: Base64 connection_id.
        :param str aes_key: Base64 AES key.

        :return: Base64 string order_id.
        """
        headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'client': 'API'}

        res = requests.post(f"{self.server_url}/newJob/", headers=headers)

        if res.status_code == 201:
            text = res.text
            text = self.decrypt_aes_ctr(text, aes_key, "string")
            return text
        else:
            raise Exception(f"Job creation failed!")


    def run_job(self, product_id, order_id, connection_id, aes_key):
        """Run a job
        
        :param str productID: Product to be executed.
        :prarm str order_id: Base64 order_id.
        :param str connection_id: Base64 connection_id.
        :param str aes_key: Base64 AES key.
        
        :return: Job run status code.
        """

        headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'client': 'api'}

        body = {
            'orderID': order_id,
            'productID': product_id
        }

        encryptedBody = self.encrypt_aes_ctr(body, aes_key, "json", "string")

        res = requests.post(f"{self.server_url}/runJob/", data=encryptedBody, headers=headers)
        if res.status_code == 202:
            return res.status_code
        else:
            raise RuntimeError("Job run failed.")


    def check_status(self, order_id, connection_id, aes_key):
        """Check job status

        :prarm str order_id: Base64 order_id.
        :param str connection_id: Base64 connection_id.
        :param str aes_key: Base64 AES key.
        
        :return: Job status message.
        """

        headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'client': 'api'}

        body = {
            'orderID': order_id,
        }

        encryptedBody = self.encrypt_aes_ctr(body, aes_key, "json", "string")

        res = requests.post(f"{self.server_url}/checkStatus/", data=encryptedBody, headers=headers)
        if res.status_code == 200:
            text = res.text
            json = self.decrypt_aes_ctr(text,aes_key,"json")
            return json
        else:
            raise RuntimeError("Status check failed.")

    def get_results(self, format, order_id, connection_id, aes_key):
        """Get job results

        :param str format: Format of file data
        :prarm str order_id: Base64 order_id.
        :param str connection_id: Base64 connection_id.
        :param str aes_key: Base64 AES key.

        :return: AES encrypted file data in specified format
        """

        headers = {'Content-type': 'text/plain', 'connection-id': connection_id, 'client': 'api'}

        body = {
            'orderID': order_id,
            'format': format
        }

        validFormats = ["TXT", "XML", "JSON"]

        if format not in validFormats:
            raise Exception("Invalid format! Valid formats include: \"TXT\", \"JSON\", \"XML\".")

        encrypted_body = self.encrypt_aes_ctr(body, aes_key, "json", "string")

        res = requests.post(f"{self.server_url}/getResults/", data=encrypted_body, headers=headers)
        
        if res.status_code == 200:
            text = res.text
            decrypted_file_data = self.decrypt_aes_ctr(text,aes_key,"string")
            return decrypted_file_data
        else:
            raise Exception(f"Result retrieval failed!")

    def encrypt_aes_ctr(self, plaintext, aes_key, format_in, format_out):
        """AES CTR encrypt plaintext

        :param JSON/str/bytes plaintext: Plaintext to be encrypted.
        :param str aes_key: Base64 AES key.
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
                raise Exception("Invalid plaintext format!")
        except Exception as e:
            raise Exception("Invalid plaintext format!")

        try:
            aes_key_bytes = base64.b64decode(aes_key)

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

        except:
            raise Exception("AES encryption failed!")   


    def decrypt_aes_ctr(self,encrypted_data, aes_key, format_out):
        """AES CTR decrypt ciphertext.

        :param str ciphertext: Ciphertext to be decrypted.
        :param str aes_key: Base64 AES key.
        :param * format_out: Format of plaintext. Default to "string".

        :return: Plaintext in requested format_out.
        """

        try:

            aes_key_bytes = base64.b64decode(aes_key)

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
        except:
            raise RuntimeError("AES decryption failed!")