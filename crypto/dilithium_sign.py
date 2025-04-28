"""
Module implementing digital signatures using CRYSTALS-Dilithium
"""

from dilithium_py.dilithium import Dilithium3
import base64

class DilithiumSigner:
    """
    Class implementing digital signatures using CRYSTALS-Dilithium
    """
    
    @staticmethod
    def generate_keypair():
        """
        Generate Dilithium key pair (public key and private key)
        
        Returns:
            Tuple (pk, sk) containing public key and private key in packed bit format
        """
        pk, sk = Dilithium3.keygen()
        return pk, sk
    
    @staticmethod
    def sign(secret_key, data):
        """
        Sign data using Dilithium private key
        
        Args:
            secret_key: Dilithium private key (in packed bit format)
            data: Data to sign (in bytes format)
            
        Returns:
            Dilithium signature (in packed bit format)
        """
        signature = Dilithium3.sign(secret_key, data)
        return signature
    
    @staticmethod
    def verify(public_key, data, signature):
        """
        Verify Dilithium signature for data
        
        Args:
            public_key: Dilithium public key (in packed bit format)
            data: Signed data (in bytes format)
            signature: Dilithium signature to verify (in packed bit format)
            
        Returns:
            True if signature is valid, False if invalid
        """
        try:
            is_valid = Dilithium3.verify(public_key, data, signature)
            return is_valid
        except Exception:
            # Catch errors if signature is invalid (e.g., wrong length)
            return False
    
    @staticmethod
    def encode_key(key):
        """
        Encode key to base64 string
        
        Args:
            key: Key in bytes format
            
        Returns:
            Base64 string
        """
        return base64.b64encode(key).decode('utf-8')
    
    @staticmethod
    def decode_key(key_b64):
        """
        Decode key from base64 string
        
        Args:
            key_b64: Base64 string
            
        Returns:
            Key in bytes format
        """
        return base64.b64decode(key_b64)