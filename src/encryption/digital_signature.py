"""
Digital signature module for the web application.
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64

class DigitalSignature:
    """Class for handling digital signatures using RSA."""
    
    def __init__(self):
        """Initialize the digital signature handler."""
        self.backend = default_backend()
    
    def generate_key_pair(self, key_size=2048):
        """
        Generate a new RSA key pair for digital signatures.
        
        Args:
            key_size (int): Size of the RSA key in bits
            
        Returns:
            tuple: (private_key, public_key) as PEM strings
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    def encrypt_private_key(self, private_key_pem, password):
        """
        Encrypt a private key with a password.
        
        Args:
            private_key_pem (str): Private key in PEM format
            password (str): Password for encryption
            
        Returns:
            str: Encrypted private key as base64 string
        """
        # Generate a random salt and initialization vector
        salt = os.urandom(16)
        iv = os.urandom(16)
        
        # Derive a key from the password
        key = self._derive_key(password.encode('utf-8'), salt)
        
        # Create an encryptor
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Pad the private key - Fixed import
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(private_key_pem.encode('utf-8')) + padder.finalize()
        
        # Encrypt the private key
        encrypted_key = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine salt, iv, and encrypted key
        result = salt + iv + encrypted_key
        
        # Return as base64
        return base64.b64encode(result).decode('utf-8')
    
    def decrypt_private_key(self, encrypted_key_base64, password):
        """
        Decrypt a private key with a password.
        
        Args:
            encrypted_key_base64 (str): Encrypted private key as base64 string
            password (str): Password for decryption
            
        Returns:
            str: Decrypted private key in PEM format
        """
        # Decode from base64
        encrypted_data = base64.b64decode(encrypted_key_base64)
        
        # Extract salt, iv, and encrypted key
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        encrypted_key = encrypted_data[32:]
        
        # Derive the key from the password
        key = self._derive_key(password.encode('utf-8'), salt)
        
        # Create a decryptor
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the private key
        padded_data = decryptor.update(encrypted_key) + decryptor.finalize()
        
        # Unpad the data - Fixed import
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        private_key_pem = unpadder.update(padded_data) + unpadder.finalize()
        
        return private_key_pem.decode('utf-8')
    
    def sign_document(self, document_data, private_key_pem):
        """
        Sign a document using a private key.
        
        Args:
            document_data (bytes): Document data to sign
            private_key_pem (str): Private key in PEM format
            
        Returns:
            bytes: Digital signature
        """
        # Load the private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=self.backend
        )
        
        # Sign the document
        signature = private_key.sign(
            document_data,
            asymmetric_padding.PSS(
                mgf=asymmetric_padding.MGF1(hashes.SHA256()),
                salt_length=asymmetric_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    def verify_signature(self, document_data, signature, public_key_pem):
        """
        Verify a document's signature using a public key.
        
        Args:
            document_data (bytes): Document data to verify
            signature (bytes): Digital signature
            public_key_pem (str): Public key in PEM format
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # Load the public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=self.backend
        )
        
        try:
            # Verify the signature
            public_key.verify(
                signature,
                document_data,
                asymmetric_padding.PSS(
                    mgf=asymmetric_padding.MGF1(hashes.SHA256()),
                    salt_length=asymmetric_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def _derive_key(self, password, salt):
        """
        Derive an encryption key from a password and salt.
        
        Args:
            password (bytes): Password
            salt (bytes): Salt
            
        Returns:
            bytes: Derived key
        """
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        
        return kdf.derive(password)
