from src.main import create_app, db
from src.models.user import User
from src.services.signature_service import SignatureService

def fix_user_keys_by_username(username, password):
    """Generate new key pair for a user with missing keys."""
    app = create_app()
    
    with app.app_context():
        # Get the user by username instead of ID
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User with username '{username}' not found")
            return
            
        print(f"Found user: {user.username} (ID: {user.id})")
        print(f"Current public key exists: {user.public_key is not None}")
        print(f"Current private key exists: {user.private_key_encrypted is not None}")
        
        # Generate new key pair
        signature_service = SignatureService()
        public_key, private_key_encrypted = signature_service.generate_key_pair(
            str(user.id),
            password
        )
        
        # Update user
        user.public_key = public_key
        user.private_key_encrypted = private_key_encrypted
        
        db.session.commit()
        
        print("Key pair generated and saved successfully")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python fix_user_keys_improved.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    fix_user_keys_by_username(username, password)