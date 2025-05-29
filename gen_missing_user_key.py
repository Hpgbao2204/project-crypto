import os
import sys
from src.models.user import User
from src.main import create_app, app
from src.services.encryption_service import EncryptionService

def generate_keys_for_user(user_id):
    """Generate ABE keys for a specific user"""
    
    app = create_app()
    with app.app_context():
        # Get the user
        user = User.query.get(user_id)
        if not user:
            print(f"User with ID {user_id} not found in database")
            return
            
        print(f"Generating keys for user: {user.username}")
        
        # Group attributes by authority
        authorities = {}
        for attr in user.attributes:
            if attr.authority_name not in authorities:
                authorities[attr.authority_name] = []
            authorities[attr.authority_name].append(attr.name)
        
        # Create encryption service
        encryption_service = EncryptionService()
        
        # Generate keys for each authority
        for authority_name, attr_list in authorities.items():
            print(f"Generating keys for authority: {authority_name} with attributes: {attr_list}")
            try:
                encryption_service.generate_user_keys(str(user_id), authority_name, attr_list)
                print(f"Generated keys for authority {authority_name}")
            except Exception as e:
                print(f"Error generating keys for authority {authority_name}: {str(e)}")
                
        print(f"Keys generated successfully for user {user.username}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])
        generate_keys_for_user(user_id)
    else:
        print("Usage: python gen_missing_user_key.py <user_id>")