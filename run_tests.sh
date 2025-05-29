#!/bin/bash
# Test script for the Secure Document System web application

# Create test directories if they don't exist
mkdir -p /home/ubuntu/martsia_project/web_app/uploads
mkdir -p /home/ubuntu/martsia_project/web_app/test_files
mkdir -p /home/ubuntu/martsia_project/web_app/test_results

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

# Function to run a test and log results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local result_file="/home/ubuntu/martsia_project/web_app/test_results/${test_name}.log"
    
    echo "Running test: $test_name"
    echo "Command: $test_command"
    echo
    
    echo "=== Test: $test_name ===" > "$result_file"
    echo "Date: $(date)" >> "$result_file"
    echo "Command: $test_command" >> "$result_file"
    echo "---" >> "$result_file"
    
    # Run the test and capture output
    eval "$test_command" >> "$result_file" 2>&1
    local status=$?
    
    echo "Exit status: $status" >> "$result_file"
    
    if [ $status -eq 0 ]; then
        echo "✅ PASS: $test_name"
        echo "PASS" >> "$result_file"
    else
        echo "❌ FAIL: $test_name"
        echo "FAIL" >> "$result_file"
    fi
    echo
}

# Create a virtual environment if it doesn't exist
if [ ! -d "/home/ubuntu/martsia_project/web_app/venv" ]; then
    echo "Creating virtual environment..."
    cd /home/ubuntu/martsia_project/web_app
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-sqlalchemy flask-login werkzeug cryptography fpdf
    pip freeze > requirements.txt
else
    echo "Using existing virtual environment."
    cd /home/ubuntu/martsia_project/web_app
    source venv/bin/activate
fi

# Run database initialization test
run_test "db_init" "cd /home/ubuntu/martsia_project/web_app && python3 -c \"
from src.main import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
\""

# Run user registration test
run_test "user_registration" "cd /home/ubuntu/martsia_project/web_app && python3 -c \"
from src.main import app, db
from src.models.user import User
from werkzeug.security import generate_password_hash
import json

with app.app_context():
    # Create test users with different roles and attributes
    test_users = [
        {
            'username': 'doctor_user',
            'email': 'doctor@example.com',
            'password': generate_password_hash('password123'),
            'role': 'reader',
            'attributes': [{'name': 'Doctor', 'authority_name': 'Hospital'}]
        },
        {
            'username': 'admin_user',
            'email': 'admin@example.com',
            'password': generate_password_hash('password123'),
            'role': 'data_owner',
            'attributes': [{'name': 'Admin', 'authority_name': 'Hospital'}]
        },
        {
            'username': 'researcher_user',
            'email': 'researcher@example.com',
            'password': generate_password_hash('password123'),
            'role': 'reader',
            'attributes': [{'name': 'Researcher', 'authority_name': 'Hospital'}]
        },
        {
            'username': 'doctor_researcher',
            'email': 'dr_researcher@example.com',
            'password': generate_password_hash('password123'),
            'role': 'data_owner',
            'attributes': [
                {'name': 'Doctor', 'authority_name': 'Hospital'},
                {'name': 'Researcher', 'authority_name': 'Hospital'}
            ]
        }
    ]
    
    for user_data in test_users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f'User {user_data[\\\"username\\\"]} already exists')
            continue
            
        # Create new user
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role']
        )
        
        # Add attributes
        for attr in user_data['attributes']:
            user.add_attribute(attr['name'], attr['authority_name'])
        
        db.session.add(user)
        print(f'Created user: {user_data[\\\"username\\\"]} with attributes: {json.dumps([{\\\"name\\\": a[\\\"name\\\"], \\\"authority\\\": a[\\\"authority_name\\\"]} for a in user_data[\\\"attributes\\\"]])}')
    
    db.session.commit()
    print('Test users created successfully')
\""

# Run digital signature key generation test
run_test "signature_key_generation" "cd /home/ubuntu/martsia_project/web_app && python3 -c \"
from src.main import app, db
from src.models.user import User
from src.encryption.digital_signature import DigitalSignature
import json

with app.app_context():
    # Get test users
    users = User.query.all()
    
    for user in users:
        # Generate signature keys
        signature = DigitalSignature()
        public_key, private_key_encrypted = signature.generate_key_pair(str(user.id), 'password123')
        
        # Update user
        user.public_key = public_key
        user.private_key_encrypted = private_key_encrypted
        
        print(f'Generated keys for user: {user.username}')
        print(f'Public key length: {len(public_key)}')
        print(f'Encrypted private key length: {len(private_key_encrypted)}')
    
    db.session.commit()
    print('Signature keys generated successfully')
\""

# Run document upload test
run_test "document_upload" "cd /home/ubuntu/martsia_project/web_app && python3 -c \"
from src.main import app, db
from src.models.user import User
from src.models.document import Document
from src.services.document_service import DocumentService
import os
import shutil

with app.app_context():
    # Get test users
    admin_user = User.query.filter_by(username='admin_user').first()
    doctor_user = User.query.filter_by(username='doctor_user').first()
    
    if not admin_user or not doctor_user:
        print('Test users not found')
        exit(1)
    
    # Create document service
    document_service = DocumentService(db)
    
    # Test text document upload
    text_file_path = '/home/ubuntu/martsia_project/web_app/test_files/test_document.txt'
    
    # Create a file-like object for testing
    class MockFile:
        def __init__(self, path):
            self.path = path
            self.filename = os.path.basename(path)
            with open(path, 'rb') as f:
                self.content = f.read()
        
        def read(self):
            return self.content
        
        def save(self, path):
            shutil.copy(self.path, path)
    
    mock_text_file = MockFile(text_file_path)
    
    # Upload document for admin user
    admin_doc = document_service.save_document(mock_text_file, admin_user.id)
    print(f'Uploaded text document for admin: {admin_doc.original_filename}, ID: {admin_doc.id}')
    
    # Upload document for doctor user
    doctor_doc = document_service.save_document(mock_text_file, doctor_user.id)
    print(f'Uploaded text document for doctor: {doctor_doc.original_filename}, ID: {doctor_doc.id}')
    
    # Test PDF document upload
    pdf_file_path = '/home/ubuntu/martsia_project/web_app/test_files/test_document.pdf'
    mock_pdf_file = MockFile(pdf_file_path)
    
    # Upload PDF for admin user
    admin_pdf = document_service.save_document(mock_pdf_file, admin_user.id)
    print(f'Uploaded PDF document for admin: {admin_pdf.original_filename}, ID: {admin_pdf.id}')
    
    print('Document uploads completed successfully')
\""

# Run encryption test
run_test "document_encryption" "cd /home/ubuntu/martsia_project/web_app && python3 -c \"
from src.main import app, db
from src.models.user import User
from src.models.document import Document
from src.services.encryption_service import EncryptionService
from src.services.document_service import DocumentService
import os

with app.app_context():
    # Get test users
    admin_user = User.query.filter_by(username='admin_user').first()
    
    if not admin_user:
        print('Admin user not found')
        exit(1)
    
    # Get admin's documents
    admin_docs = Document.query.filter_by(user_id=admin_user.id, doc_type='original').all()
    
    if not admin_docs:
        print('No documents found for admin user')
        exit(1)
    
    # Create services
    encryption_service = EncryptionService()
    document_service = DocumentService(db)
    
    # Test Hybrid ABE encryption
    doc_to_encrypt = admin_docs[0]
    access_policy = 'Doctor@Hospital OR Admin@Hospital'
    
    encrypted_path = encryption_service.encrypt_document(
        doc_to_encrypt.get_file_path(),
        'hybrid',
        access_policy
    )
    
    if not encrypted_path:
        print('Encryption failed')
        exit(1)
    
    # Save encrypted document
    encrypted_doc = document_service.save_encrypted_document(
        doc_to_encrypt.id,
        os.path.basename(encrypted_path),
        'hybrid',
        access_policy,
        admin_user.id
    )
    
    print(f'Encrypted document with Hybrid ABE: {encrypted_doc.original_filename}, ID: {encrypted_doc.id}')
    print(f'Access policy: {encrypted_doc.access_policy}')
    
    # If there's another document, test MA-ABE encryption
    if len(admin_docs) > 1:
        doc_to_encrypt = admin_docs[1]
        access_policy = 'Doctor@Hospital AND Researcher@Hospital'
        
        encrypted_path = encryption_service.encrypt_document(
            doc_to_encrypt.get_file_path(),
            'maabe',
            access_policy
        )
        
        if not encrypted_path:
            print('MA-ABE encryption failed')
        else:
            # Save encrypted document
            encrypted_doc = document_service.save_encrypted_document(
                doc_to_encrypt.id,
                os.path.basename(encrypted_path),
                'maabe',
                access_policy,
                admin_user.id
            )
            
            print(f'Encrypted document with MA-ABE: {encrypted_doc.original_filename}, ID: {encrypted_doc.id}')
            print(f'Access policy: {encrypted_doc.access_policy}')
    
    print('Encryption tests completed successfully')
\""

# Run decryption test - Fixed f-string syntax error
run_test "document_decryption" "cd /home/ubuntu/martsia_project/web_app && python3 -c \"
from src.main import app, db
from src.models.user import User
from src.models.document import Document
from src.services.encryption_service import EncryptionService
from src.services.document_service import DocumentService
import os

with app.app_context():
    # Get test users
    doctor_user = User.query.filter_by(username='doctor_user').first()
    doctor_researcher = User.query.filter_by(username='doctor_researcher').first()
    
    if not doctor_user or not doctor_researcher:
        print('Test users not found')
        exit(1)
    
    # Get encrypted documents
    encrypted_docs = Document.query.filter_by(doc_type='encrypted').all()
    
    if not encrypted_docs:
        print('No encrypted documents found')
        exit(1)
    
    # Create services
    encryption_service = EncryptionService()
    document_service = DocumentService(db)
    
    # Test decryption with doctor user (should succeed for 'Doctor OR Admin' policy)
    doc_to_decrypt = encrypted_docs[0]
    
    print(f'Attempting to decrypt document {doc_to_decrypt.id} with user {doctor_user.username}')
    print(f'Document access policy: {doc_to_decrypt.access_policy}')
    # Fixed f-string syntax
    print(f'User attributes: {[f\\\"{attr.name}@{attr.authority_name}\\\" for attr in doctor_user.attributes]}')
    
    decrypted_path = encryption_service.decrypt_document(
        doc_to_decrypt.get_file_path(),
        doc_to_decrypt.encryption_method,
        doctor_user.attributes
    )
    
    if decrypted_path:
        print(f'✅ Decryption succeeded for {doctor_user.username}')
    else:
        print(f'❌ Decryption failed for {doctor_user.username}')
    
    # Test decryption with doctor_researcher user (should succeed for both policies)
    for doc in encrypted_docs:
        print(f'Attempting to decrypt document {doc.id} with user {doctor_researcher.username}')
        print(f'Document access policy: {doc.access_policy}')
        # Fixed f-string syntax
        print(f'User attributes: {[f\\\"{attr.name}@{attr.authority_name}\\\" for attr in doctor_researcher.attributes]}')
        
        decrypted_path = encryption_service.decrypt_document(
            doc.get_file_path(),
            doc.encryption_method,
            doctor_researcher.attributes
        )
        
        if decrypted_path:
            print(f'✅ Decryption succeeded for {doctor_researcher.username}')
        else:
            print(f'❌ Decryption failed for {doctor_researcher.username}')
    
    print('Decryption tests completed')
\""

# Run digital signature test
run_test "digital_signature" "cd /home/ubuntu/martsia_project/web_app && python3 -c \"
from src.main import app, db
from src.models.user import User
from src.models.document import Document
from src.services.signature_service import SignatureService
from src.services.document_service import DocumentService
import os

with app.app_context():
    # Get test users
    admin_user = User.query.filter_by(username='admin_user').first()
    doctor_user = User.query.filter_by(username='doctor_user').first()
    
    if not admin_user or not doctor_user:
        print('Test users not found')
        exit(1)
    
    # Get admin's original documents
    admin_docs = Document.query.filter_by(user_id=admin_user.id, doc_type='original').all()
    
    if not admin_docs:
        print('No documents found for admin user')
        exit(1)
    
    # Create services
    signature_service = SignatureService()
    document_service = DocumentService(db)
    
    # Test signing document
    doc_to_sign = admin_docs[0]
    
    signature_path, metadata = signature_service.sign_document(
        doc_to_sign.get_file_path(),
        str(admin_user.id),
        'password123',
        admin_user.private_key_encrypted
    )
    
    if not signature_path:
        print('Signing failed')
        exit(1)
    
    # Save signed document
    signed_doc = document_service.save_signed_document(
        doc_to_sign.id,
        os.path.basename(signature_path),
        admin_user.id
    )
    
    print(f'Signed document: {signed_doc.original_filename}, ID: {signed_doc.id}')
    
    # Test verifying signature (should succeed)
    is_valid = signature_service.verify_signature(
        signed_doc.get_file_path(),
        signed_doc.get_signature_path(),
        admin_user.public_key
    )
    
    if is_valid:
        print('✅ Signature verification succeeded with correct key')
    else:
        print('❌ Signature verification failed with correct key')
    
    # Test verifying with wrong key (should fail)
    is_valid = signature_service.verify_signature(
        signed_doc.get_file_path(),
        signed_doc.get_signature_path(),
        doctor_user.public_key
    )
    
    if not is_valid:
        print('✅ Signature verification correctly failed with wrong key')
    else:
        print('❌ Signature verification incorrectly succeeded with wrong key')
    
    print('Digital signature tests completed')
\""

# Generate test summary
echo "Generating test summary..."
echo

echo "=== Test Summary ===" > /home/ubuntu/martsia_project/web_app/test_results/summary.md
echo "Date: $(date)" >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
echo >> /home/ubuntu/martsia_project/web_app/test_results/summary.md

echo "| Test | Status |" >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
echo "|------|--------|" >> /home/ubuntu/martsia_project/web_app/test_results/summary.md

for result_file in /home/ubuntu/martsia_project/web_app/test_results/*.log; do
    test_name=$(basename "$result_file" .log)
    if grep -q "PASS" "$result_file"; then
        echo "| $test_name | ✅ PASS |" >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
    else
        echo "| $test_name | ❌ FAIL |" >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
    fi
done

echo >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
echo "## Detailed Results" >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
echo >> /home/ubuntu/martsia_project/web_app/test_results/summary.md

for result_file in /home/ubuntu/martsia_project/web_app/test_results/*.log; do
    test_name=$(basename "$result_file" .log)
    echo "### $test_name" >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
    echo '```' >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
    cat "$result_file" >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
    echo '```' >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
    echo >> /home/ubuntu/martsia_project/web_app/test_results/summary.md
done

echo "Test summary generated: /home/ubuntu/martsia_project/web_app/test_results/summary.md"
echo
echo "=== Test Execution Completed ==="
