"""
User authentication service using PKI
"""

import os
import json
import time
from crypto.pki_auth import PKIAuth

class AuthService:
    """
    User authentication service
    """
    
    def __init__(self, storage_dir='/app/data', ca_file='ca.pem'):
        """
        Initialize authentication service
        
        Args:
            storage_dir: Data storage directory
            ca_file: CA file name
        """
        self.storage_dir = storage_dir
        self.ca_file = os.path.join(storage_dir, ca_file)
        self.users_file = os.path.join(storage_dir, 'users.json')
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize PKI
        self.pki = PKIAuth(key_size=2048)
        
        # Load CA from file if it exists
        if os.path.exists(self.ca_file):
            self.pki.deserialize_from_file(self.ca_file)
        else:
            # Save new CA to file
            self.pki.serialize_to_file(self.ca_file)
        
        # Load user list
        self.users = self._load_users()
        
        # Store authentication challenges
        self.auth_challenges = {}
    
    def _load_users(self):
        """
        Load user list from file
        
        Returns:
            Dict containing user information
        """
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        """
        Save user list to file
        """
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def register_user(self, user_id, full_name, phone, expiry_days=365):
        """
        Register new user
        
        Args:
            user_id: User ID (email)
            full_name: Full name
            phone: Phone number
            expiry_days: Expiration time (days)
            
        Returns:
            Dict containing user information
        """
        # Check if user already exists
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        # Create keys and certificate for user
        user_keys = self.pki.generate_user_keys(user_id, expiry_days)
        
        # Add additional information
        user_info = {
            **user_keys,
            'full_name': full_name,
            'phone': phone
        }
        
        # Save user information
        self.users[user_id] = user_info
        self._save_users()
        
        return user_info
    
    def get_user(self, user_id):
        """
        Get user information
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing user information
        """
        if user_id not in self.users:
            raise ValueError(f"User {user_id} does not exist")
        
        return self.users[user_id]
    
    def authenticate_user(self, user_id, challenge_response=None):
        """
        Authenticate user
        
        Args:
            user_id: User ID
            challenge_response: Challenge response (optional)
            
        Returns:
            Tuple (success, response) containing authentication result and response
        """
        try:
            # Check if user exists
            if user_id not in self.users:
                return False, {'error': f"User {user_id} does not exist"}
            
            user_info = self.users[user_id]
            
            # If no challenge response, create new challenge
            if challenge_response is None:
                success, response = self.pki.authenticate_user(user_info)
                
                if success:
                    # Save challenge
                    challenge_id = os.urandom(16).hex()
                    self.auth_challenges[challenge_id] = {
                        'user_id': user_id,
                        'challenge': response['challenge'],
                        'created_at': int(time.time())
                    }
                    
                    # Return challenge and ID
                    return True, {
                        'challenge_id': challenge_id,
                        'encrypted_challenge': response['challenge']['encrypted_challenge']
                    }
                
                return success, response
            
            # Authenticate challenge response
            if 'challenge_id' not in challenge_response:
                return False, {'error': 'Missing challenge ID'}
            
            challenge_id = challenge_response['challenge_id']
            
            # Check if challenge exists
            if challenge_id not in self.auth_challenges:
                return False, {'error': 'Challenge does not exist or has expired'}
            
            # Get challenge information
            challenge_info = self.auth_challenges[challenge_id]
            
            # Check user
            if challenge_info['user_id'] != user_id:
                return False, {'error': 'Challenge does not match user'}
            
            # Check expiration time (5 minutes)
            current_time = int(time.time())
            if current_time - challenge_info['created_at'] > 300:
                # Delete expired challenge
                del self.auth_challenges[challenge_id]
                return False, {'error': 'Challenge has expired'}
            
            # Authenticate response
            decrypted_challenge = self.pki.decrypt_challenge(
                user_info['private_key'],
                challenge_info['challenge']['encrypted_challenge']
            )
            
            # Check response
            if decrypted_challenge == challenge_info['challenge']['original_text']:
                # Delete used challenge
                del self.auth_challenges[challenge_id]
                return True, {'message': 'Authentication successful'}
            
            return False, {'error': 'Authentication failed'}
            
        except Exception as e:
            return False, {'error': f'Authentication error: {str(e)}'}
    
    def revoke_user(self, user_id):
        """
        Revoke user
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        if user_id not in self.users:
            raise ValueError(f"User {user_id} does not exist")
        
        # Delete user
        del self.users[user_id]
        self._save_users()
        
        return True