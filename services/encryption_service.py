"""
Module implementing encryption service using hybrid encryption
"""

import os
import json
import time
from crypto.hybrid_encryption import HybridEncryption

class EncryptionService:
    """
    Data encryption service
    """
    
    def __init__(self, auth_service):
        """
        Initialize encryption service
        
        Args:
            auth_service: Authentication service
        """
        self.auth_service = auth_service
        self.hybrid_encryption = HybridEncryption()
    
    def encrypt_data(self, recipient_id, data, associated_data=None):
        """
        Encrypt data for recipient
        
        Args:
            recipient_id: Recipient ID
            data: Data to encrypt (bytes or str)
            associated_data: Associated data (bytes or str, optional)
            
        Returns:
            Dict containing encrypted data
        """
        # Get recipient information
        recipient_info = self.auth_service.get_user(recipient_id)
        
        # Convert data to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if associated_data is not None and isinstance(associated_data, str):
            associated_data = associated_data.encode('utf-8')
        
        # Encrypt data
        encrypted_data = self.hybrid_encryption.encrypt(
            recipient_info['certificate'],
            data,
            associated_data
        )
        
        # Add metadata
        result = {
            **encrypted_data,
            'recipient_id': recipient_id,
            'timestamp': int(time.time())
        }
        
        return result
    
    def decrypt_data(self, recipient_id, encrypted_data, associated_data=None):
        """
        Decrypt data
        
        Args:
            recipient_id: Recipient ID
            encrypted_data: Dict containing encrypted data
            associated_data: Associated data (bytes or str, optional)
            
        Returns:
            Decrypted data (bytes)
        """
        # Check recipient
        if encrypted_data.get('recipient_id') != recipient_id:
            raise ValueError("Data not encrypted for this recipient")
        
        # Get recipient information
        recipient_info = self.auth_service.get_user(recipient_id)
        
        # Convert associated data to bytes if needed
        if associated_data is not None and isinstance(associated_data, str):
            associated_data = associated_data.encode('utf-8')
        
        # Decrypt data
        decrypted_data = self.hybrid_encryption.decrypt(
            recipient_info['private_key'],
            encrypted_data,
            associated_data
        )
        
        return decrypted_data
    
    def encrypt_payment_info(self, recipient_id, payment_info, transaction_id):
        """
        Encrypt payment information
        
        Args:
            recipient_id: Recipient ID
            payment_info: Dict containing payment information
            transaction_id: Transaction ID
            
        Returns:
            Dict containing encrypted payment information
        """
        # Convert payment information to JSON
        payment_data = json.dumps(payment_info).encode('utf-8')
        
        # Use transaction ID as associated data
        associated_data = transaction_id.encode('utf-8')
        
        # Encrypt data
        encrypted_payment = self.encrypt_data(
            recipient_id,
            payment_data,
            associated_data
        )
        
        return encrypted_payment
    
    def decrypt_payment_info(self, recipient_id, encrypted_payment, transaction_id):
        """
        Decrypt payment information
        
        Args:
            recipient_id: Recipient ID
            encrypted_payment: Dict containing encrypted payment information
            transaction_id: Transaction ID
            
        Returns:
            Dict containing payment information
        """
        # Use transaction ID as associated data
        associated_data = transaction_id.encode('utf-8')
        
        # Decrypt data
        decrypted_data = self.decrypt_data(
            recipient_id,
            encrypted_payment,
            associated_data
        )
        
        # Convert JSON to dict
        payment_info = json.loads(decrypted_data.decode('utf-8'))
        
        return payment_info