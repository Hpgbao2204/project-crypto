"""
Demo setup script for the ABE document security system.
"""

import os
import json
import shutil
from datetime import datetime
from flask import current_app

from src.main import app, db
from src.models.user import User
from src.models.user import Attribute, User
from src.models.document import Document
from src.services.encryption_service import EncryptionService
from src.services.signature_service import SignatureService
from src.services.document_service import DocumentService

# Sample data
AUTHORITIES = ['Hospital', 'University', 'Government']
ATTRIBUTES = {
    'Hospital': ['Doctor', 'Nurse', 'Patient', 'Admin'],
    'University': ['Professor', 'Student', 'Staff', 'Researcher'],
    'Government': ['Officer', 'Director', 'Citizen', 'Contractor']
}
USERS = [
    {
        'username': 'alice_doctor',
        'email': 'alice@hospital.com',
        'password': 'password123',
        'attributes': [('Doctor', 'Hospital'), ('Researcher', 'University')]
    },
    {
        'username': 'bob_professor',
        'email': 'bob@university.com',
        'password': 'password123',
        'attributes': [('Professor', 'University'), ('Researcher', 'University')]
    },
    {
        'username': 'charlie_admin',
        'email': 'charlie@hospital.com',
        'password': 'password123',
        'attributes': [('Admin', 'Hospital'), ('Staff', 'University')]
    },
    {
        'username': 'david_officer',
        'email': 'david@gov.com',
        'password': 'password123',
        'attributes': [('Officer', 'Government'), ('Citizen', 'Government')]
    }
]

DOCUMENTS = [
    {
        'name': 'Medical Research Protocol',
        'content': 'This is a confidential medical research protocol.',
        'policy': '(Doctor@Hospital AND Researcher@University) OR Admin@Hospital',
        'owner': 'alice_doctor'
    },
    {
        'name': 'University Grant Proposal',
        'content': 'Proposal for a new research grant in the university.',
        'policy': 'Professor@University OR Researcher@University',
        'owner': 'bob_professor'
    },
    {
        'name': 'Hospital Admin Document',
        'content': 'Administrative document for hospital management.',
        'policy': 'Admin@Hospital',
        'owner': 'charlie_admin'
    },
    {
        'name': 'Government Report',
        'content': 'Confidential government report.',
        'policy': 'Officer@Government AND Director@Government',
        'owner': 'david_officer'
    }
]

def setup_demo():
    """Set up the demo environment."""
    with app.app_context():
        print("Setting up demo environment...")
        
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Clear uploaded files directory
        upload_dir = app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        else:
            os.makedirs(upload_dir)
        
        # Create encryption service
        encryption_service = EncryptionService()
        signature_service = SignatureService()
        document_service = DocumentService(db)
        
        # Set up authorities
        print("Setting up authorities...")
        for authority_name in AUTHORITIES:
            encryption_service.setup_authority(authority_name)
            
            # Add attributes for this authority
            for attr_name in ATTRIBUTES[authority_name]:
                attribute = Attribute(name=attr_name, authority_name=authority_name)
                db.session.add(attribute)
        
        # Create users
        print("Creating users...")
        for user_data in USERS:
            user = User(
                username=user_data['username'],
                email=user_data['email']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            db.session.flush()  # To get user ID
            
            # Generate signature keys
            public_key, private_key = signature_service.generate_key_pair(str(user.id), user_data['password'])
            user.public_key = public_key
            
            # Store private key securely (in production would be done differently)
            key_path = os.path.join(upload_dir, f"user_{user.id}_private_key.enc")
            with open(key_path, 'wb') as f:
                f.write(private_key.encode('utf-8'))
            
            # Assign attributes to user
            for attr_name, authority_name in user_data['attributes']:
                attribute = Attribute.query.filter_by(
                    name=attr_name, 
                    authority_name=authority_name
                ).first()
                
                if attribute:
                    user.attributes.append(attribute)
                    
                    # Generate encryption keys for this attribute
                    encryption_service.generate_user_keys(str(user.id), authority_name, [attr_name])
        
        db.session.commit()
        
        # Create and encrypt documents
        print("Creating and encrypting documents...")
        for doc_data in DOCUMENTS:
            # Find the owner
            owner = User.query.filter_by(username=doc_data['owner']).first()
            
            if not owner:
                print(f"Owner {doc_data['owner']} not found, skipping document")
                continue
            
            # Create temporary file with content
            doc_path = os.path.join(upload_dir, f"temp_{doc_data['name'].replace(' ', '_')}.txt")
            with open(doc_path, 'w') as f:
                f.write(doc_data['content'])
            
            # Save original document
            with open(doc_path, 'rb') as f:
                document = document_service.save_document_from_file(f, owner.id, doc_data['name'])
            
            # Encrypt document
            encrypted_path = encryption_service.encrypt_document(
                document.get_file_path(),
                'hybrid',
                doc_data['policy'],
                str(owner.id)
            )
            
            if encrypted_path:
                # Save encrypted document
                document_service.save_encrypted_document(
                    document.id,
                    os.path.basename(encrypted_path),
                    'hybrid',
                    doc_data['policy'],
                    owner.id
                )
                print(f"Document '{doc_data['name']}' encrypted successfully")
            else:
                print(f"Failed to encrypt document '{doc_data['name']}'")
            
            # Clean up temp file
            if os.path.exists(doc_path):
                os.unlink(doc_path)
        
        print("Demo setup complete.")

def add_document_service_method():
    """
    Thêm phương thức save_document_from_file cho DocumentService,
    đồng thời chuyển BufferedReader (file_obj) thành đối tượng có filename và save().
    """
    # Tạo 1 class nhỏ để “gói” file_handle từ disk kèm thuộc tính `filename` và `save()`
    class DummyFile:
        def __init__(self, file_handle, filename):
            # file_handle là object _io.BufferedReader đã được mở (rb)
            self._file = file_handle
            # filename bạn truyền vào khi gọi save_document_from_file()
            self.filename = filename
            # content_type có thể để None, save_uploaded_file sẽ mặc định kiểu MIME
            self.content_type = None

        def save(self, dst_path):
            # Mỗi lần save, rewind về đầu rồi ghi toàn bộ nội dung file vào đường dẫn dst_path
            self._file.seek(0)
            with open(dst_path, 'wb') as out:
                out.write(self._file.read())

    # Hàm thực sự được trả về cho DocumentService.save_document_from_file
    def save_document_from_file(self, file_obj, user_id, filename):
        # file_obj là một _io.BufferedReader bình thường, filename là tên gốc chúng ta muốn gán
        dummy = DummyFile(file_obj, filename)
        # Gọi tiếp vào save_document với dummy thay vì file_obj trực tiếp
        return self.save_document(dummy, user_id)

    DocumentService.save_document_from_file = save_document_from_file



if __name__ == "__main__":
    add_document_service_method()
    setup_demo()