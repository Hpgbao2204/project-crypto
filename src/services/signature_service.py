"""
Signature service for the web application.
"""

import os
import json
import base64
from datetime import datetime
from flask import current_app
from src.encryption.digital_signature import DigitalSignature
from src.utils.file_utils import get_file_path, save_json_data, load_json_data

class SignatureService:
    """Service for handling digital signature operations."""
    
    def __init__(self):
        """Initialize the signature service."""
        self.digital_signature = DigitalSignature()
    
    def generate_key_pair(self, user_id, password):
        """
        Generate a new key pair for digital signatures.
        
        Args:
            user_id (str): User identifier
            password (str): Password to encrypt the private key
            
        Returns:
            tuple: (public_key, encrypted_private_key)
        """
        # Generate key pair
        private_key, public_key = self.digital_signature.generate_key_pair()
        
        # Encrypt private key
        encrypted_private_key = self.digital_signature.encrypt_private_key(private_key, password)
        
        return public_key, encrypted_private_key
    
    def sign_document(self, document_path, user_id, password, encrypted_private_key):
        """
        Sign a document using a user's private key.
        
        Args:
            document_path (str): Path to the document to sign
            user_id (str): User identifier
            password (str): Password to decrypt the private key
            encrypted_private_key (str): Encrypted private key
            
        Returns:
            tuple: (signature_path, metadata)
        """
        try:
            # Decrypt private key
            private_key = self.digital_signature.decrypt_private_key(encrypted_private_key, password)
            
            # Read document
            with open(document_path, 'rb') as f:
                document_data = f.read()
            
            # Sign document
            signature = self.digital_signature.sign_document(document_data, private_key)
            
            # Save signature
            signature_filename = f"signature_{os.path.basename(document_path)}.sig"
            signature_path = os.path.join(current_app.config['UPLOAD_FOLDER'], signature_filename)
            
            with open(signature_path, 'wb') as f:
                f.write(signature)
            
            # Create metadata
            metadata = {
                'document': os.path.basename(document_path),
                'signature': signature_filename,
                'signer_id': user_id,
                'timestamp': str(datetime.now())
            }
            
            # Save metadata
            metadata_filename = f"signature_{os.path.basename(document_path)}.json"
            metadata_path = os.path.join(current_app.config['UPLOAD_FOLDER'], metadata_filename)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return signature_path, metadata
            
        except Exception as e:
            current_app.logger.error(f"Signing failed: {str(e)}")
            return None, None
    
    def verify_signature(self, document_path, signature_path, public_key):
        """
        Verify a document's signature.
        
        Args:
            document_path (str): Path to the document
            signature_path (str): Path to the signature
            public_key (str): Public key in PEM format
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Read document
            with open(document_path, 'rb') as f:
                document_data = f.read()
            
            # Read signature
            with open(signature_path, 'rb') as f:
                signature = f.read()
            
            # Verify signature
            return self.digital_signature.verify_signature(document_data, signature, public_key)
            
        except Exception as e:
            current_app.logger.error(f"Verification failed: {str(e)}")
            return False
