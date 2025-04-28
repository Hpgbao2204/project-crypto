"""
Module implementing digital signature service using CRYSTALS-Dilithium
"""

import os
import json
import time
import base64
from dilithium_py.dilithium import Dilithium3

class SignatureService:
    """
    Digital signature service
    """
    
    def __init__(self, auth_service, storage_dir="/app/data"):
        """
        Initialize the digital signature service
        
        Args:
            auth_service: Authentication service
            storage_dir: Directory for key storage
        """
        self.auth_service = auth_service
        self.storage_dir = storage_dir
        self.keys_file = os.path.join(storage_dir, "dilithium_keys.json")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load Dilithium keys
        self.dilithium_keys = self._load_keys()
    
    def _load_keys(self):
        """
        Load Dilithium keys from file
        
        Returns:
            Dict containing users' Dilithium keys
        """
        if os.path.exists(self.keys_file):
            with open(self.keys_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_keys(self):
        """
        Save Dilithium keys to file
        """
        with open(self.keys_file, "w") as f:
            json.dump(self.dilithium_keys, f, indent=2)
    
    def generate_user_keys(self, user_id):
        """
        Generate Dilithium key pair for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing public and private keys (in base64 format)
        """
        # Check if keys already exist
        if user_id in self.dilithium_keys:
            return self.dilithium_keys[user_id]
        
        # Generate keys
        pk, sk = Dilithium3.keygen()
        
        # Save keys
        keys = {
            "public_key": base64.b64encode(pk).decode("utf-8"),
            "secret_key": base64.b64encode(sk).decode("utf-8")
        }
        self.dilithium_keys[user_id] = keys
        self._save_keys()
        
        return keys

    def get_public_key(self, user_id):
        """
        Get a user's Dilithium public key
        
        Args:
            user_id: User ID
            
        Returns:
            Public key in base64 format
        """
        if user_id not in self.dilithium_keys:
            # Automatically generate if not found
            self.generate_user_keys(user_id)
            # raise ValueError(f"Dilithium keys not found for user {user_id}")
        
        return self.dilithium_keys[user_id]["public_key"]

    def sign_data(self, user_id, data):
        """
        Sign data using a user's Dilithium private key
        
        Args:
            user_id: User ID
            data: Data to sign (bytes)
            
        Returns:
            Signature in base64 format
        """
        if user_id not in self.dilithium_keys:
            # Automatically generate if not found
            self.generate_user_keys(user_id)
            # raise ValueError(f"Dilithium keys not found for user {user_id}")
            
        secret_key_b64 = self.dilithium_keys[user_id]["secret_key"]
        secret_key = base64.b64decode(secret_key_b64)
        
        signature = Dilithium3.sign(secret_key, data)
        return base64.b64encode(signature).decode("utf-8")

    def verify_signature(self, user_id, data, signature_b64):
        """
        Verify signature using a user's Dilithium public key
        
        Args:
            user_id: User ID
            data: Signed data (bytes)
            signature_b64: Signature to verify (in base64 format)
            
        Returns:
            True if signature is valid, False if invalid
        """
        public_key_b64 = self.get_public_key(user_id)
        public_key = base64.b64decode(public_key_b64)
        signature = base64.b64decode(signature_b64)
        
        try:
            is_valid = Dilithium3.verify(public_key, data, signature)
            return is_valid
        except Exception:
            # Catch errors if signature is invalid (e.g., wrong length)
            return False