import os
import json
from src.main import create_app, db
from src.models.user import User
from src.services.encryption_service import EncryptionService

def fix_user_keys(username):
    """Create a complete key file with all attributes for a user."""
    app = create_app()
    
    with app.app_context():
        # Get the user
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User with username '{username}' not found")
            return
            
        print(f"Found user: {user.username} (ID: {user.id})")
        
        # Group attributes by authority
        authorities = {}
        for attr in user.attributes:
            auth_name = attr.authority_name
            if auth_name not in authorities:
                authorities[auth_name] = []
            authorities[auth_name].append(attr.name)
        
        print(f"User attributes: {authorities}")
        
        # Create encryption service
        encryption_service = EncryptionService()
        gp = encryption_service.get_global_parameters()
        
        # Final user keys structure
        user_keys = {
            'GID': str(user.id),
            'keys': {},
            'authority_keys': {}
        }
        
        # Generate keys for each authority
        for authority_name, attr_list in authorities.items():
            print(f"Processing authority: {authority_name} with attributes: {attr_list}")
            
            # Get authority secret key
            sk_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{authority_name}_sk.json")
            if not os.path.exists(sk_path):
                print(f"Setting up new authority: {authority_name}")
                encryption_service.setup_authority(authority_name)
            
            with open(sk_path, 'r') as f:
                sk = json.load(f)
            
            # Format attributes as "attribute@authority"
            formatted_attributes = [f"{attr}@{authority_name}" for attr in attr_list]
            
            # Generate keys for each attribute
            attr_keys = encryption_service.hybrid_abe.multiple_attributes_keygen(
                gp, sk, str(user.id), formatted_attributes
            )
            
            # Add to user keys structure
            user_keys['keys'].update(attr_keys)
            user_keys['authority_keys'][authority_name] = sk['key']
        
        # Save complete user keys
        keys_path = os.path.join(app.config['UPLOAD_FOLDER'], f"user_{user.id}_keys.json")
        with open(keys_path, 'w') as f:
            json.dump(user_keys, f, indent=2)
        
        print(f"Complete key file generated for user {user.username}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python fix_all_user_keys.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    fix_user_keys(username)