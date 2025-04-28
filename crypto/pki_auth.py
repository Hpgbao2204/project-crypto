"""
Module implementing authentication based on traditional PKI as an alternative to IB-PKC
"""

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509 import Name, NameAttribute, CertificateBuilder, random_serial_number
from cryptography.x509.oid import NameOID
import datetime
import os
import base64
import json
import time

class PKIAuth:
    """
    Class implementing authentication based on traditional PKI
    """
    
    def __init__(self, key_size=2048, use_ecc=False):
        """
        Initialize the PKI system
        
        Args:
            key_size: RSA key size (bits)
            use_ecc: Use ECC instead of RSA
        """
        self.key_size = key_size
        self.use_ecc = use_ecc
        
        # Create CA key and certificate if not already existing
        self.ca_private_key, self.ca_certificate = self._create_ca()
    
    def _create_ca(self):
        """
        Create Certificate Authority (CA) key and certificate
        
        Returns:
            Tuple (private_key, certificate) of CA
        """
        # Create private key
        if self.use_ecc:
            private_key = ec.generate_private_key(ec.SECP384R1())
        else:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size
            )
        
        # Create certificate
        subject = issuer = Name([
            NameAttribute(NameOID.COUNTRY_NAME, "VN"),
            NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Hanoi"),
            NameAttribute(NameOID.LOCALITY_NAME, "Hanoi"),
            NameAttribute(NameOID.ORGANIZATION_NAME, "Secure Transaction System"),
            NameAttribute(NameOID.COMMON_NAME, "Secure Transaction CA"),
        ])
        
        # Create certificate
        certificate = CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)  # 10 years
        ).sign(private_key, hashes.SHA256())
        
        return private_key, certificate
    
    def generate_user_keys(self, user_id, expiry_days=365):
        """
        Create keys and certificate for user
        
        Args:
            user_id: User ID (email)
            expiry_days: Expiration time (days)
            
        Returns:
            Dict containing key and certificate information
        """
        # Create private key
        if self.use_ecc:
            private_key = ec.generate_private_key(ec.SECP384R1())
        else:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size
            )
        
        # Create certificate
        subject = Name([
            NameAttribute(NameOID.COUNTRY_NAME, "VN"),
            NameAttribute(NameOID.ORGANIZATION_NAME, "Secure Transaction System"),
            NameAttribute(NameOID.COMMON_NAME, user_id),
        ])
        
        # Create certificate
        certificate = CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.ca_certificate.issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=expiry_days)
        ).sign(self.ca_private_key, hashes.SHA256())
        
        # Serialize private key
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize certificate
        certificate_pem = certificate.public_bytes(
            encoding=serialization.Encoding.PEM
        )
        
        # Create user information
        current_time = int(time.time())
        expiry_time = current_time + (expiry_days * 24 * 60 * 60)
        
        user_info = {
            'user_id': user_id,
            'private_key': base64.b64encode(private_key_pem).decode('utf-8'),
            'certificate': base64.b64encode(certificate_pem).decode('utf-8'),
            'created_at': current_time,
            'expires_at': expiry_time
        }
        
        return user_info
    
    def encrypt_challenge(self, certificate_pem_b64, challenge_text):
        """
        Encrypt challenge for user
        
        Args:
            certificate_pem_b64: User certificate in base64 format
            challenge_text: Challenge to encrypt
            
        Returns:
            Dict containing encrypted challenge
        """
        # Deserialize certificate
        certificate_pem = base64.b64decode(certificate_pem_b64)
        certificate = x509.load_pem_x509_certificate(certificate_pem)
        
        # Get public key
        public_key = certificate.public_key()
        
        # Encrypt challenge
        if isinstance(public_key, rsa.RSAPublicKey):
            encrypted_challenge = public_key.encrypt(
                challenge_text.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        else:  # ECC
            # With ECC, we need to use ECIES (not directly supported)
            # This is a simple implementation, in practice should use ECIES library
            # Or use hybrid encryption with AES
            raise NotImplementedError("ECC encryption not implemented in this example")
        
        return {
            'encrypted_challenge': base64.b64encode(encrypted_challenge).decode('utf-8'),
            'original_text': challenge_text
        }
    
    def decrypt_challenge(self, private_key_pem_b64, encrypted_challenge_b64):
        """
        Decrypt challenge
        
        Args:
            private_key_pem_b64: Private key in base64 format
            encrypted_challenge_b64: Encrypted challenge in base64 format
            
        Returns:
            Decrypted challenge
        """
        # Deserialize private key
        private_key_pem = base64.b64decode(private_key_pem_b64)
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
        
        # Deserialize encrypted challenge
        encrypted_challenge = base64.b64decode(encrypted_challenge_b64)
        
        # Decrypt challenge
        if isinstance(private_key, rsa.RSAPrivateKey):
            decrypted_challenge = private_key.decrypt(
                encrypted_challenge,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        else:  # ECC
            raise NotImplementedError("ECC decryption not implemented in this example")
        
        return decrypted_challenge.decode('utf-8')
    
    def authenticate_user(self, user_info, challenge=None):
        """
        Authenticate user by decrypting challenge
        
        Args:
            user_info: User information (including private key and certificate)
            challenge: Encrypted challenge (optional, create new if none)
            
        Returns:
            Tuple (success, response) containing authentication result and response
        """
        try:
            # Check expiration time
            current_time = int(time.time())
            if current_time > user_info['expires_at']:
                return False, {'error': 'Key has expired'}
            
            # Create challenge if none exists
            if challenge is None:
                # Create random challenge
                challenge_text = os.urandom(32).hex()
                challenge = self.encrypt_challenge(
                    user_info['certificate'],
                    challenge_text
                )
                
                return True, {'challenge': challenge}
            
            # Decrypt challenge
            decrypted_challenge = self.decrypt_challenge(
                user_info['private_key'],
                challenge['encrypted_challenge']
            )
            
            # Check challenge
            if decrypted_challenge == challenge['original_text']:
                return True, {'message': 'Authentication successful'}
            else:
                return False, {'error': 'Authentication failed'}
            
        except Exception as e:
            return False, {'error': f'Authentication error: {str(e)}'}
    
    def serialize_to_file(self, filename):
        """
        Save CA key and certificate to file
        
        Args:
            filename: File name
        """
        # Serialize CA private key
        ca_private_key_pem = self.ca_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize CA certificate
        ca_certificate_pem = self.ca_certificate.public_bytes(
            encoding=serialization.Encoding.PEM
        )
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(ca_private_key_pem)
            f.write(ca_certificate_pem)
    
    def deserialize_from_file(self, filename):
        """
        Read CA key and certificate from file
        
        Args:
            filename: File name
        """
        with open(filename, 'rb') as f:
            data = f.read()
        
        # Separate private key and certificate
        private_key_data, certificate_data = data.split(b'-----BEGIN CERTIFICATE-----')
        certificate_data = b'-----BEGIN CERTIFICATE-----' + certificate_data
        
        # Deserialize private key
        self.ca_private_key = serialization.load_pem_private_key(
            private_key_data,
            password=None
        )
        
        # Deserialize certificate
        # self.ca_certificate = serialization.load_pem_x509_certificate(
        #     certificate_data
        # )
        self.ca_certificate = x509.load_pem_x509_certificate(
            certificate_data
        )