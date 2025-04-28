"""
Flask demo application for Secure Transaction System
"""

from flask import Flask, request, jsonify
import os
import json
import time
import base64

# Import services
from services.auth_service import AuthService
from services.encryption_service import EncryptionService
from services.signature_service import SignatureService

# Initialize Flask application
app = Flask(__name__)

# Configure data directory
DATA_DIR = "/app/data"

# Initialize services
auth_service = AuthService(storage_dir=DATA_DIR)
encryption_service = EncryptionService(auth_service)
signature_service = SignatureService(auth_service, storage_dir=DATA_DIR)

# Store transactions (in memory for demo)
transactions = {}

# --- Helper Functions ---

def get_auth_token():
    """Get authentication token from header (simple example)"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

def verify_auth_token(token):
    """Authenticate token (simple example, returns user_id)"""
    # In this demo, token is the user_id
    try:
        user_info = auth_service.get_user(token)
        return token
    except ValueError:
        return None

# --- API Endpoints ---

@app.route("/")
def index():
    return jsonify({"message": "Welcome to the Safe Trading System Demo!"})

# --- User Management ---

@app.route("/register", methods=["POST"])
def register():
    """New User Registration"""
    data = request.get_json()
    if not data or "user_id" not in data or "full_name" not in data or "phone" not in data:
        return jsonify({"error": "Missing registration information"}), 400
    
    try:
        user_info = auth_service.register_user(
            data["user_id"],
            data["full_name"],
            data["phone"]
        )
        # Generate Dilithium keys during registration
        signature_service.generate_user_keys(data["user_id"])
        
        # Only return public information
        public_info = {
            "user_id": user_info["user_id"],
            "certificate": user_info["certificate"],
            "dilithium_public_key": signature_service.get_public_key(data["user_id"])
        }
        return jsonify(public_info), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # Conflict
    except Exception as e:
        return jsonify({"error": f"Registration error: {str(e)}"}), 500

@app.route("/users/<user_id>", methods=["GET"])
def get_user_info(user_id):
    """Get user public information"""
    try:
        user_info = auth_service.get_user(user_id)
        public_info = {
            "user_id": user_info["user_id"],
            "certificate": user_info["certificate"],
            "dilithium_public_key": signature_service.get_public_key(user_id)
        }
        return jsonify(public_info)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Error retrieving user information: {str(e)}"}), 500

# --- Authentication ---

@app.route("/auth/challenge", methods=["POST"])
def request_challenge():
    """Authentication challenge request"""
    data = request.get_json()
    if not data or "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    try:
        success, response = auth_service.authenticate_user(data["user_id"])
        if success:
            return jsonify(response)
        else:
            return jsonify(response), 401 # Unauthorized
    except Exception as e:
        return jsonify({"error": f"Error creating challenge: {str(e)}"}), 500

@app.route("/auth/login", methods=["POST"])
def login_with_challenge():
    """Login by solving the challenge"""
    data = request.get_json()
    if not data or "user_id" not in data or "challenge_id" not in data or "decrypted_challenge" not in data:
        return jsonify({"error": "Missing login information"}), 400

    user_id = data["user_id"]
    challenge_id = data["challenge_id"]
    decrypted_challenge_from_user = data["decrypted_challenge"]

    try:
        # Get the original saved challenge
        if challenge_id not in auth_service.auth_challenges:
            return jsonify({"error": "The challenge does not exist or has expired."}), 401
        
        challenge_info = auth_service.auth_challenges[challenge_id]
        
        # Check user and time
        current_time = int(time.time())
        if challenge_info["user_id"] != user_id:
            return jsonify({"error": "Challenge does not match user"}), 401
        if current_time - challenge_info["created_at"] > 300: # 5 minutes
            del auth_service.auth_challenges[challenge_id]
            return jsonify({"error": "Challenge has expired"}), 401

        # Compare user response with original challenge
        if decrypted_challenge_from_user == challenge_info["challenge"]["original_text"]:
            # Delete used challenge
            del auth_service.auth_challenges[challenge_id]
            # Create token (simple example: user_id)
            token = user_id 
            return jsonify({"message": "Login successful", "token": token})
        else:
            return jsonify({"error": "Authentication failed"}), 401

    except Exception as e:
        return jsonify({"error": f"Login error: {str(e)}"}), 500

# --- Transactions ---

@app.route("/transactions", methods=["POST"])
def create_transaction():
    """Create new transaction"""
    token = get_auth_token()
    sender_id = verify_auth_token(token)
    if not sender_id:
        return jsonify({"error": "Authentication required"}), 401
        
    data = request.get_json()
    if not data or "recipient_id" not in data or "amount" not in data:
        return jsonify({"error": "Missing transaction information"}), 400
    
    recipient_id = data["recipient_id"]
    amount = data["amount"]
    currency = data.get("currency", "VND")
    metadata = data.get("metadata", {})
    
    try:
        # Check if recipient exists
        auth_service.get_user(recipient_id)
        
        # Create transaction ID
        tx_id = os.urandom(16).hex()
        
        # Create transaction data
        transaction_data = {
            "transaction_id": tx_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "amount": amount,
            "currency": currency,
            "metadata": metadata,
            "timestamp": int(time.time()),
            "status": "created",
            "signature": None, # Signature will be added later
            "encrypted_payment": None # Encrypted payment information
        }
        
        # Save transaction (in memory)
        transactions[tx_id] = transaction_data
        
        return jsonify({"message": "Transaction created", "transaction_id": tx_id}), 201
        
    except ValueError as e: # Recipient doesn't exist
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Error creating transaction: {str(e)}"}), 500

@app.route("/transactions/<tx_id>", methods=["GET"])
def get_transaction(tx_id):
    """Get transaction information"""
    if tx_id not in transactions:
        return jsonify({"error": "Transaction does not exist"}), 404
    
    # Return a copy to avoid direct modification
    return jsonify(transactions[tx_id].copy())

def prepare_data_for_signing(transaction):
    """Prepare transaction data for signing (remove signature and sort)"""
    data_to_sign = transaction.copy()
    data_to_sign.pop("signature", None)
    data_to_sign.pop("encrypted_payment", None) # Don't sign encrypted part
    # Sort keys to ensure consistency
    return json.dumps(data_to_sign, sort_keys=True).encode("utf-8")

@app.route("/transactions/<tx_id>/sign", methods=["POST"])
def sign_transaction(tx_id):
    """Sign transaction"""
    token = get_auth_token()
    user_id = verify_auth_token(token)
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
        
    if tx_id not in transactions:
        return jsonify({"error": "Transaction does not exist"}), 404
        
    transaction = transactions[tx_id]
    
    # Only sender can sign
    if transaction["sender_id"] != user_id:
        return jsonify({"error": "No permission to sign this transaction"}), 403
        
    if transaction["signature"] is not None:
        return jsonify({"error": "Transaction already signed"}), 409
        
    try:
        # Prepare data for signing
        data_to_sign = prepare_data_for_signing(transaction)
        
        # Sign data
        signature_b64 = signature_service.sign_data(user_id, data_to_sign)
        
        # Update transaction
        transaction["signature"] = signature_b64
        transaction["status"] = "signed"
        
        return jsonify({"message": "Transaction signed successfully", "signature": signature_b64})
        
    except Exception as e:
        return jsonify({"error": f"Error signing transaction: {str(e)}"}), 500

@app.route("/transactions/<tx_id>/verify", methods=["POST"])
def verify_transaction_signature(tx_id):
    """Verify transaction signature"""
    if tx_id not in transactions:
        return jsonify({"error": "Transaction does not exist"}), 404
        
    transaction = transactions[tx_id]
    
    if transaction["signature"] is None:
        return jsonify({"error": "Transaction has not been signed"}), 400
        
    try:
        # Prepare signed data
        data_signed = prepare_data_for_signing(transaction)
        
        # Verify signature
        is_valid = signature_service.verify_signature(
            transaction["sender_id"],
            data_signed,
            transaction["signature"]
        )
        
        if is_valid:
            return jsonify({"message": "Signature valid"})
        else:
            return jsonify({"error": "Signature invalid"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Error verifying signature: {str(e)}"}), 500

# --- Payment Encryption ---

@app.route("/transactions/<tx_id>/encrypt_payment", methods=["POST"])
def encrypt_payment_info_for_transaction(tx_id):
    """Encrypt payment information for transaction"""
    token = get_auth_token()
    user_id = verify_auth_token(token)
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
        
    if tx_id not in transactions:
        return jsonify({"error": "Transaction does not exist"}), 404
        
    transaction = transactions[tx_id]
    
    # Only sender can encrypt payment
    if transaction["sender_id"] != user_id:
        return jsonify({"error": "No permission to encrypt payment for this transaction"}), 403
        
    data = request.get_json()
    if not data or "payment_info" not in data:
        return jsonify({"error": "Missing payment information"}), 400
        
    payment_info = data["payment_info"]
    recipient_id = transaction["recipient_id"]
    
    try:
        encrypted_payment = encryption_service.encrypt_payment_info(
            recipient_id,
            payment_info,
            tx_id # Use tx_id as associated data
        )
        
        # Update transaction
        transaction["encrypted_payment"] = encrypted_payment
        transaction["status"] = "payment_encrypted"
        
        return jsonify({"message": "Payment information has been encrypted", "encrypted_payment": encrypted_payment})
        
    except Exception as e:
        return jsonify({"error": f"Error encrypting payment information: {str(e)}"}), 500

@app.route("/transactions/<tx_id>/decrypt_payment", methods=["POST"])
def decrypt_payment_info_for_transaction(tx_id):
    """Decrypt payment information (recipient only)"""
    token = get_auth_token()
    user_id = verify_auth_token(token)
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
        
    if tx_id not in transactions:
        return jsonify({"error": "Transaction does not exist"}), 404
        
    transaction = transactions[tx_id]
    
    # Only recipient can decrypt
    if transaction["recipient_id"] != user_id:
        return jsonify({"error": "No permission to decrypt payment for this transaction"}), 403
        
    if transaction["encrypted_payment"] is None:
        return jsonify({"error": "Transaction has no encrypted payment information"}), 400
        
    try:
        decrypted_payment = encryption_service.decrypt_payment_info(
            user_id,
            transaction["encrypted_payment"],
            tx_id # Use tx_id as associated data
        )
        
        # Update status (example)
        transaction["status"] = "payment_decrypted"
        
        return jsonify({"message": "Payment information successfully decrypted", "payment_info": decrypted_payment})
        
    except Exception as e:
        return jsonify({"error": f"Error decrypting payment information: {str(e)}"}), 500

# --- Main Execution ---

if __name__ == "__main__":
    # Run on 0.0.0.0 to be accessible from outside the container
    app.run(host="0.0.0.0", port=5000, debug=True) # Debug=True for development environment