"""
Encryption service for the web application.
"""

import os
import json
import base64
from datetime import datetime
from flask import current_app
from src.encryption.hybrid_abe import HybridABE
from src.utils.file_utils import get_file_path, save_json_data, load_json_data

class EncryptionService:
    """Service for handling encryption and decryption operations."""
    
    def __init__(self):
        """Initialize the encryption service."""
        self.hybrid_abe = HybridABE()
        
        # Ensure global parameters exist
        self._ensure_global_parameters()
    
    def _ensure_global_parameters(self):
        """Ensure global parameters for encryption exist."""
        params_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'hybrid_params.json')
        
        if not os.path.exists(params_path):
            # Generate new global parameters
            gp = self.hybrid_abe.setup()
            
            # Save parameters
            with open(params_path, 'w') as f:
                json.dump(gp, f, indent=2)
    
    def get_global_parameters(self):
        """
        Get global parameters for encryption.
        
        Returns:
            dict: Global parameters
        """
        params_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'hybrid_params.json')
        
        with open(params_path, 'r') as f:
            return json.load(f)
    
    def setup_authority(self, authority_name):
        """
        Set up an authority for attribute-based encryption.
        
        Args:
            authority_name (str): Name of the authority
            
        Returns:
            tuple: (public_key, secret_key)
        """
        # Get global parameters
        gp = self.get_global_parameters()
        
        # Generate authority keys
        pk, sk = self.hybrid_abe.authsetup(gp, authority_name)
        
        # Save keys
        pk_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{authority_name}_pk.json")
        sk_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{authority_name}_sk.json")
        
        with open(pk_path, 'w') as f:
            json.dump(pk, f, indent=2)
        
        with open(sk_path, 'w') as f:
            json.dump(sk, f, indent=2)
        
        return pk, sk
    
    def generate_user_keys(self, user_id, authority_name, attributes):
        """
        Generate encryption keys for a user.
        
        Args:
            user_id (str): User identifier
            authority_name (str): Authority name
            attributes (list): List of attributes
            
        Returns:
            dict: User keys
        """
        # Get global parameters
        gp = self.get_global_parameters()
        
        # Check if authority exists, if not set it up
        sk_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{authority_name}_sk.json")
        if not os.path.exists(sk_path):
            current_app.logger.info(f"Setting up new authority: {authority_name}")
            self.setup_authority(authority_name)
        
        # Get authority secret key
        with open(sk_path, 'r') as f:
            sk = json.load(f)
        
        # Generate user keys
        user_keys = {}
        
        # Format attributes as "attribute@authority"
        formatted_attributes = [f"{attr}@{authority_name}" for attr in attributes]
        
        # Generate keys for each attribute
        attr_keys = self.hybrid_abe.multiple_attributes_keygen(gp, sk, user_id, formatted_attributes)
        
        # Create user key structure
        user_keys = {
            'GID': user_id,
            'keys': attr_keys,
            'authority_keys': {
                authority_name: sk['key']
            }
        }
        
        # Save user keys
        keys_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"user_{user_id}_keys.json")
        
        # Remove the line that was causing an error (user is not defined)
        if os.path.exists(keys_path):
            current_app.logger.info(f"Keys already exist for user {user_id}")
        
        with open(keys_path, 'w') as f:
            json.dump(user_keys, f, indent=2)
        
        return user_keys
    
    def encrypt_file(self, input_file_path, policy, user_id):
        """
        Encrypt a file using Hybrid ABE.
        
        Args:
            input_file_path (str): Path to the input file
            policy (str): Access policy string
            user_id (str): User identifier
            
        Returns:
            tuple: (encrypted_file_path, metadata)
        """
        # Get global parameters
        gp = self.get_global_parameters()
        
        # Get public keys of authorities
        pks = {}
        authorities_dir = current_app.config['UPLOAD_FOLDER']
        
        # Find all authority public keys
        for filename in os.listdir(authorities_dir):
            if filename.endswith('_pk.json'):
                with open(os.path.join(authorities_dir, filename), 'r') as f:
                    pk = json.load(f)
                    pks[pk['name']] = pk
        
        # Read the input file
        with open(input_file_path, 'rb') as f:
            file_data = f.read()
        
        # Encrypt the file
        encrypted_data = self.hybrid_abe.encrypt(gp, pks, file_data, policy)
        
        # Generate output filename
        output_filename = f"encrypted_{os.path.basename(input_file_path)}.json"
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
        
        # Save the encrypted file
        with open(output_path, 'w') as f:
            json.dump(encrypted_data, f)
        
        # Return metadata
        metadata = {
            'original_file': os.path.basename(input_file_path),
            'encrypted_file': output_filename,
            'policy': policy,
            'encryption_method': 'hybrid',
            'user_id': user_id,
            'timestamp': str(datetime.now())
        }
        
        return output_path, metadata
    
    def decrypt_file(self, encrypted_file_path, user_id):
        """
        Decrypt a file using Hybrid ABE.
        
        Args:
            encrypted_file_path (str): Path to the encrypted file
            user_id (str): User identifier
            
        Returns:
            tuple: (decrypted_file_path, success)
        """
        # Get global parameters
        gp = self.get_global_parameters()
        
        # Get user keys
        keys_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"user_{user_id}_keys.json")
        
        with open(keys_path, 'r') as f:
            sk = json.load(f)
        
        # Load the encrypted file
        with open(encrypted_file_path, 'r') as f:
            encrypted_data = json.load(f)
        
        try:
            # Decrypt the file
            decrypted_data = self.hybrid_abe.decrypt(gp, sk, encrypted_data)
            
            # Generate output filename
            output_filename = f"decrypted_{os.path.basename(encrypted_file_path).replace('.json', '')}"
            output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
            
            # Save the decrypted file
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path, True
            
        except Exception as e:
            current_app.logger.error(f"Decryption failed: {str(e)}")
            return None, False
    
    def decrypt_document(self, file_path, encryption_method, user_attributes):
        """
        Decrypt a document using the appropriate encryption method.
        
        Args:
            file_path (str): Path to the encrypted file
            encryption_method (str): Encryption method used ('hybrid' or 'maabe')
            user_attributes (list): List of user attributes
            
        Returns:
            str: Path to the decrypted file, or None if decryption failed
        """
        try:
            # For testing purposes, create a user ID from attributes
            user_id = str(hash(''.join([f"{attr.name}@{attr.authority_name}" for attr in user_attributes])))
            
            # Create temporary user keys if needed
            self._ensure_user_keys(user_id, user_attributes)
            
            # Decrypt based on encryption method
            if encryption_method == 'hybrid':
                # Use hybrid ABE decryption
                decrypted_path, success = self.decrypt_file(file_path, user_id)
                if success:
                    return decrypted_path
                return None
            elif encryption_method == 'maabe':
                # For testing, we'll simulate MA-ABE decryption
                # In a real implementation, this would use the MA-ABE library
                output_filename = f"decrypted_maabe_{os.path.basename(file_path)}"
                output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
                
                # Copy the file for testing (in real app, would decrypt)
                with open(file_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                
                return output_path
            else:
                current_app.logger.error(f"Unknown encryption method: {encryption_method}")
                return None
        except Exception as e:
            current_app.logger.error(f"Decryption error: {str(e)}")
            return None
    
    def _ensure_user_keys(self, user_id, user_attributes):
        """
        Ensure user keys exist for testing.
        
        Args:
            user_id (str): User identifier
            user_attributes (list): List of user attributes
        """
        keys_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"user_{user_id}_keys.json")
        
        if not os.path.exists(keys_path):
            # Create dummy keys for testing
            gp = self.get_global_parameters()
            
            # Create authority keys if needed
            authorities = set()
            for attr in user_attributes:
                authorities.add(attr.authority_name)
            
            for authority in authorities:
                auth_sk_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{authority}_sk.json")
                if not os.path.exists(auth_sk_path):
                    self.setup_authority(authority)
            
            # Generate user keys for each authority
            for authority in authorities:
                attrs = [attr.name for attr in user_attributes if attr.authority_name == authority]
                if attrs:
                    self.generate_user_keys(user_id, authority, attrs)
