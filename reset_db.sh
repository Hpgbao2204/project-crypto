#!/bin/bash
# Reset and seed database for testing

echo "=== Resetting and Seeding Database ==="
echo "Date: $(date)"
echo

# Create necessary directories
mkdir -p /home/ubuntu/martsia_project/web_app/uploads
mkdir -p /home/ubuntu/martsia_project/web_app/test_files
mkdir -p /home/ubuntu/martsia_project/web_app/instance

# Remove existing database
rm -f /home/ubuntu/martsia_project/web_app/instance/app.db

# Create test files
echo "Creating test files..."
cd /home/ubuntu/martsia_project/web_app/test_files

# Create a simple text file
cat > test_document.txt << EOF
This is a test document for the Secure Document System.
It will be used to test encryption, decryption, and digital signatures.

CONFIDENTIAL INFORMATION
Patient: John Doe
ID: 12345
Diagnosis: Test Condition
Treatment: Test Medication
EOF

# Create a simple PDF file using Python
python3 -c "
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(40, 10, 'Test PDF Document')
pdf.ln(20)
pdf.set_font('Arial', '', 12)
pdf.multi_cell(0, 10, 'This is a test PDF document for the Secure Document System. It will be used to test encryption, decryption, and digital signatures.\n\nCONFIDENTIAL INFORMATION\nPatient: Jane Doe\nID: 67890\nDiagnosis: Test Condition\nTreatment: Test Medication')
pdf.output('test_document.pdf', 'F')
"

echo "Test files created successfully."

# Initialize and seed database
cd /home/ubuntu/martsia_project/web_app
source venv/bin/activate

python3 -c "
from src.main import app, db
from src.models.user import User, Attribute
from src.models.document import Document
from src.encryption.digital_signature import DigitalSignature
from werkzeug.security import generate_password_hash
import os
import shutil
import json

with app.app_context():
    # Create database tables
    db.drop_all()
    db.create_all()
    print('Database initialized successfully')
    
    # Create attributes
    attributes = [
        {'name': 'Doctor', 'authority_name': 'Hospital', 'description': 'Medical doctor'},
        {'name': 'Nurse', 'authority_name': 'Hospital', 'description': 'Registered nurse'},
        {'name': 'Admin', 'authority_name': 'Hospital', 'description': 'Hospital administrator'},
        {'name': 'Researcher', 'authority_name': 'Hospital', 'description': 'Medical researcher'}
    ]
    
    for attr_data in attributes:
        attr = Attribute(
            name=attr_data['name'],
            authority_name=attr_data['authority_name'],
            description=attr_data['description']
        )
        db.session.add(attr)
    
    db.session.commit()
    print('Attributes created successfully')
    
    # Create test users
    test_users = [
        {
            'username': 'doctor_user',
            'email': 'doctor@example.com',
            'password': 'password123',
            'role': 'reader',
            'attributes': [{'name': 'Doctor', 'authority_name': 'Hospital'}]
        },
        {
            'username': 'admin_user',
            'email': 'admin@example.com',
            'password': 'password123',
            'role': 'data_owner',
            'attributes': [{'name': 'Admin', 'authority_name': 'Hospital'}]
        },
        {
            'username': 'researcher_user',
            'email': 'researcher@example.com',
            'password': 'password123',
            'role': 'reader',
            'attributes': [{'name': 'Researcher', 'authority_name': 'Hospital'}]
        },
        {
            'username': 'doctor_researcher',
            'email': 'dr_researcher@example.com',
            'password': 'password123',
            'role': 'data_owner',
            'attributes': [
                {'name': 'Doctor', 'authority_name': 'Hospital'},
                {'name': 'Researcher', 'authority_name': 'Hospital'}
            ]
        }
    ]
    
    created_users = {}
    
    for user_data in test_users:
        # Create new user
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=generate_password_hash(user_data['password']),
            role=user_data['role']
        )
        
        # Add attributes
        for attr in user_data['attributes']:
            attribute = Attribute.query.filter_by(
                name=attr['name'], 
                authority_name=attr['authority_name']
            ).first()
            if attribute:
                user.attributes.append(attribute)
        
        db.session.add(user)
        db.session.flush()  # Get ID without committing
        
        # Generate signature keys - Fixed to match the actual method signature
        signature = DigitalSignature()
        private_key, public_key = signature.generate_key_pair()
        
        # Encrypt the private key with the user's password
        private_key_encrypted = signature.encrypt_private_key(private_key, user_data['password'])
        
        user.public_key = public_key
        user.private_key_encrypted = private_key_encrypted
        
        created_users[user_data['username']] = user
        
        print(f'Created user: {user.username} with attributes: {[attr.name + \"@\" + attr.authority_name for attr in user.attributes]}')
    
    db.session.commit()
    print('Test users created successfully')
    
    # Upload test documents
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    # Function to create a document
    def create_document(file_path, user, doc_type='original'):
        filename = os.path.basename(file_path)
        file_type = os.path.splitext(filename)[1][1:].lower()
        
        # Copy file to uploads folder
        dest_filename = f\"{user.id}_{int(time.time())}_{filename}\"
        dest_path = os.path.join(upload_folder, dest_filename)
        shutil.copy(file_path, dest_path)
        
        # Create document record
        doc = Document(
            filename=dest_filename,
            original_filename=filename,
            file_type=file_type,
            file_size=os.path.getsize(dest_path),
            doc_type=doc_type,
            user_id=user.id
        )
        
        db.session.add(doc)
        db.session.flush()  # Get ID without committing
        return doc
    
    import time
    
    # Upload documents for admin user
    admin_user = created_users['admin_user']
    doctor_user = created_users['doctor_user']
    
    # Text document for admin
    text_file_path = '/home/ubuntu/martsia_project/web_app/test_files/test_document.txt'
    admin_text_doc = create_document(text_file_path, admin_user)
    print(f'Created text document for admin: {admin_text_doc.original_filename}, ID: {admin_text_doc.id}')
    
    # PDF document for admin
    pdf_file_path = '/home/ubuntu/martsia_project/web_app/test_files/test_document.pdf'
    admin_pdf_doc = create_document(pdf_file_path, admin_user)
    print(f'Created PDF document for admin: {admin_pdf_doc.original_filename}, ID: {admin_pdf_doc.id}')
    
    # Text document for doctor
    doctor_text_doc = create_document(text_file_path, doctor_user)
    print(f'Created text document for doctor: {doctor_text_doc.original_filename}, ID: {doctor_text_doc.id}')
    
    db.session.commit()
    print('Test documents created successfully')
    
    # Create encrypted documents
    from src.encryption.hybrid_abe import HybridABE
    
    # Function to encrypt a document
    def encrypt_document(doc, encryption_method, access_policy):
        # Get source file path
        source_path = os.path.join(upload_folder, doc.filename)
        
        # Create encrypted file name
        encrypted_filename = f\"encrypted_{doc.id}_{int(time.time())}_{doc.original_filename}\"
        encrypted_path = os.path.join(upload_folder, encrypted_filename)
        
        # Encrypt file based on method
        if encryption_method == 'hybrid':
            encryptor = HybridABE()
            encryptor.encrypt_file(source_path, encrypted_path, access_policy)
        else:
            # For testing, just copy the file (in real app, would use MA-ABE)
            shutil.copy(source_path, encrypted_path)
        
        # Create encrypted document record
        encrypted_doc = Document(
            filename=encrypted_filename,
            original_filename=doc.original_filename,
            file_type=doc.file_type,
            file_size=os.path.getsize(encrypted_path),
            doc_type='encrypted',
            encryption_method=encryption_method,
            access_policy=access_policy,
            user_id=doc.user_id,
            parent_id=doc.id
        )
        
        db.session.add(encrypted_doc)
        db.session.flush()
        return encrypted_doc
    
    # Encrypt admin's text document with Hybrid ABE
    admin_text_encrypted = encrypt_document(
        admin_text_doc,
        'hybrid',
        'Doctor@Hospital OR Admin@Hospital'
    )
    print(f'Created encrypted document: {admin_text_encrypted.original_filename}, ID: {admin_text_encrypted.id}')
    print(f'Access policy: {admin_text_encrypted.access_policy}')
    
    # Encrypt admin's PDF document with 'MA-ABE' (simulated)
    admin_pdf_encrypted = encrypt_document(
        admin_pdf_doc,
        'maabe',
        'Doctor@Hospital AND Researcher@Hospital'
    )
    print(f'Created encrypted document: {admin_pdf_encrypted.original_filename}, ID: {admin_pdf_encrypted.id}')
    print(f'Access policy: {admin_pdf_encrypted.access_policy}')
    
    db.session.commit()
    print('Encrypted documents created successfully')
    
    # Create signed documents
    from src.encryption.digital_signature import DigitalSignature
    
    # Function to sign a document
    def sign_document(doc, user, password):
        # Get source file path
        source_path = os.path.join(upload_folder, doc.filename)
        
        # Create signature file name
        signature_filename = f\"sig_{doc.id}_{int(time.time())}.sig\"
        signature_path = os.path.join(upload_folder, signature_filename)
        
        # Sign document - First decrypt the private key
        signer = DigitalSignature()
        private_key = signer.decrypt_private_key(user.private_key_encrypted, password)
        
        # Read file content
        with open(source_path, 'rb') as f:
            document_data = f.read()
        
        # Sign the document
        signature_data = signer.sign_document(document_data, private_key)
        
        # Save signature to file
        with open(signature_path, 'wb') as f:
            f.write(signature_data)
        
        # Update document record
        doc.is_signed = True
        doc.signature_file = signature_filename
        doc.signer_id = user.id
        
        return doc
    
    # Sign admin's text document
    admin_text_signed = sign_document(admin_text_doc, admin_user, 'password123')
    print(f'Signed document: {admin_text_signed.original_filename}, ID: {admin_text_signed.id}')
    
    db.session.commit()
    print('Signed documents created successfully')
    
    print('Database seeding completed successfully')
"

echo "=== Database Reset and Seeding Completed ==="
