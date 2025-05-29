#!/bin/bash
# Test script for the Secure Document System web application

# Create test directories if they don't exist
mkdir -p /home/ubuntu/martsia_project/web_app/uploads
mkdir -p /home/ubuntu/martsia_project/web_app/test_files

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

# Create a virtual environment if it doesn't exist
if [ ! -d "/home/ubuntu/martsia_project/web_app/venv" ]; then
    echo "Creating virtual environment..."
    cd /home/ubuntu/martsia_project/web_app
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-sqlalchemy flask-login werkzeug cryptography
    pip freeze > requirements.txt
else
    echo "Virtual environment already exists."
    cd /home/ubuntu/martsia_project/web_app
    source venv/bin/activate
fi

# Run the Flask application
echo "Starting the Flask application..."
cd /home/ubuntu/martsia_project/web_app
export FLASK_APP=src/main.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
