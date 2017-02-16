import hashlib
from Crypto.Cipher import AES
import base64

class PonyCrypto(object):
    def __init__(self, kms_key_arn, client):
        """
            Initalize with KMS Key ARN
        """
        self.kms_key_arn = kms_key_arn
        self.client = client

    def encrypt(self, payload):
        """
            Encrypts the file in a data envelope using
            provided data key and CMK returns ciphertext
        """

        data_key = self.__generate_data_key()
        encypted_payload = self.__encrypt_with_aes(
            data_key['Plaintext'],
            payload
        )

        result = {
            'ciphertext_key': data_key['CiphertextBlob'],
            'payload': encypted_payload
        }

        return result

    def hash_payload(self, payload):
        """
            Returns a hash of the payload for storage
            with the asset if necessary
        """
        h = hashlib.new('sha256')
        h.update(payload)
        payload_hash = h.hexdigest()
        return payload_hash

    def __encrypt_with_aes(self, plaintext_key, payload):
        """
            Takes a data key and returns ciphertext for
            use in public encrypt method
        """
        str_payload = str(payload)
        pad = lambda s: s + (32 - len(s) % 32) * ' '
        crypter = AES.new(plaintext_key)
        ciphertext = base64.b64encode(crypter.encrypt(pad(str_payload)))
        return ciphertext

    def __generate_data_key(self):
        """
            Returns a data key for the KMS ARN
        """
        response = self.client.generate_data_key(
            KeyId=self.kms_key_arn,
            KeySpec='AES_128'
        )
        return response
