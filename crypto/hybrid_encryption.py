"""
Module implementing hybrid encryption using PKI and AES-GCM
"""

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64

class HybridEncryption:
    """
    Class implementing hybrid encryption (PKI + AES-GCM)
    """
    
    def encrypt(self, certificate_pem_b64, data, associated_data=None):
        """
        Encrypt data using hybrid encryption
        
        Args:
            certificate_pem_b64: Recipient's certificate in base64 format
            data: Data to encrypt (bytes)
            associated_data: Associated data (bytes, optional)
            
        Returns:
            Dict containing encrypted data
        """
        # Deserialize certificate
        certificate_pem = base64.b64decode(certificate_pem_b64)
        certificate = serialization.load_pem_x509_certificate(certificate_pem)
        
        # Get public key
        public_key = certificate.public_key()
        
        # 1. Generate random AES session key
        aes_key = os.urandom(32)  # AES-256
        
        # 2. Encrypt session key with recipient's public key (RSA)
        # Note: Only RSA is supported in this example
        if not isinstance(public_key, serialization.load_pem_public_key(b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq+\n...").__class__):
             raise TypeError("Only RSA session key encryption is supported in this example")
             
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 3. Encrypt data with AES-GCM
        iv = os.urandom(12)  # GCM recommends 12-byte IV
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        
        # Add associated data if available
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)
            
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag
        
        # 4. Package the result
        return {
            'encrypted_key': base64.b64encode(encrypted_key).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8')
        }

    def decrypt(self, private_key_pem_b64, encrypted_data, associated_data=None):
        """
        Decrypt data using hybrid encryption
        
        Args:
            private_key_pem_b64: Recipient's private key in base64 format
            encrypted_data: Dict containing encrypted data
            associated_data: Associated data (bytes, optional)
            
        Returns:
            Decrypted data (bytes)
        """
        # Deserialize private key
        private_key_pem = base64.b64decode(private_key_pem_b64)
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
        
        # 1. Decrypt AES session key with private key (RSA)
        encrypted_key = base64.b64decode(encrypted_data['encrypted_key'])
        
        if not isinstance(private_key, serialization.load_pem_private_key(b"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCq+\n...").__class__):
            raise TypeError("Only RSA session key decryption is supported in this example")
            
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 2. Decrypt data with AES-GCM
        iv = base64.b64decode(encrypted_data['iv'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        tag = base64.b64decode(encrypted_data['tag'])
        
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        
        # Add associated data if available
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)
            
        # Decrypt and authenticate
        try:
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            return decrypted_data
        except Exception as e:
            raise ValueError(f"Decryption or authentication failed: {str(e)}")