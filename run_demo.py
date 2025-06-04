"""
Demo script for the ABE document security system.
"""

import os
from flask import current_app
from tabulate import tabulate

from src.main import app, db
from src.models.user import User, Attribute
from src.models.document import Document
from src.services.encryption_service import EncryptionService
from src.services.document_service import DocumentService

def run_demo():
    """Run the demo application flow."""
    with app.app_context():
        print("\n===== SECURE DOCUMENT SYSTEM DEMO =====\n")
        
        # Get services
        encryption_service = EncryptionService()
        document_service = DocumentService(db)
        
        # List all users
        users = User.query.all()
        user_data = []
        for user in users:
            # Thay vì dùng user.user_attributes, ta dùng trực tiếp user.attributes
            attrs = [f"{a.name}@{a.authority_name}" for a in user.attributes]
            user_data.append([user.id, user.username, user.email, ", ".join(attrs)])
        
        print("\n=== USERS IN THE SYSTEM ===")
        print(tabulate(user_data, headers=["ID", "Username", "Email", "Attributes"]))
        
        # List all documents
        documents = Document.query.filter_by(doc_type='encrypted').all()
        doc_data = []
        for doc in documents:
            owner = User.query.get(doc.user_id)
            doc_data.append([
                doc.id, 
                doc.original_filename, 
                owner.username if owner else "Unknown", 
                doc.encryption_method,
                doc.access_policy
            ])
        
        print("\n=== ENCRYPTED DOCUMENTS ===")
        print(tabulate(doc_data, headers=["ID", "Filename", "Owner", "Enc Method", "Access Policy"]))
        
        # Demo: Test access to documents
        print("\n=== TESTING DOCUMENT ACCESS ===")
        
        # Define test cases: (user_id, document_id, expected_result)
        test_cases = []
        
        # Alice (Doctor@Hospital, Researcher@University) accessing various documents
        alice = User.query.filter_by(username='alice_doctor').first()
        
        # Bob (Professor@University, Researcher@University) accessing documents
        bob = User.query.filter_by(username='bob_professor').first()
        
        # Charlie (Admin@Hospital, Staff@University) accessing documents
        charlie = User.query.filter_by(username='charlie_admin').first()
        
        # David (Officer@Government, Citizen@Government) accessing documents
        david = User.query.filter_by(username='david_officer').first()
        
        # Create test cases based on available users and documents
        if alice and bob and charlie and david:
            for doc in documents:
                if "Medical" in doc.original_filename:
                    # Alice và Charlie nên truy cập được tài liệu y tế
                    test_cases.append((alice.id, doc.id, True))
                    test_cases.append((charlie.id, doc.id, True))  
                    test_cases.append((bob.id, doc.id, False))
                    test_cases.append((david.id, doc.id, False))
                    
                elif "University" in doc.original_filename:
                    # Bob và Alice (với vai trò Researcher) nên truy cập được tài liệu trường đại học
                    test_cases.append((bob.id, doc.id, True))
                    test_cases.append((alice.id, doc.id, True))
                    test_cases.append((charlie.id, doc.id, False))
                    test_cases.append((david.id, doc.id, False))
                    
                elif "Hospital Admin" in doc.original_filename:
                    # Chỉ Charlie (Admin@Hospital) mới truy cập được tài liệu quản trị bệnh viện
                    test_cases.append((charlie.id, doc.id, True))
                    test_cases.append((alice.id, doc.id, False))
                    test_cases.append((bob.id, doc.id, False))
                    test_cases.append((david.id, doc.id, False))
                    
                elif "Government" in doc.original_filename:
                    # David chưa có attribute Director nên sẽ không truy cập được
                    test_cases.append((david.id, doc.id, False))
                    test_cases.append((alice.id, doc.id, False))
                    test_cases.append((bob.id, doc.id, False))
                    test_cases.append((charlie.id, doc.id, False))
        
        # Run the access tests
        test_results = []
        for user_id, doc_id, expected in test_cases:
            user = User.query.get(user_id)
            doc = Document.query.get(doc_id)
            
            if not user or not doc:
                continue
                
            # Thu thập các Attribute của user
            user_attrs = []
            for a in user.attributes:
                user_attrs.append(a)
            
            # Thử giải mã
            decrypted_path = encryption_service.decrypt_document(
                doc.get_file_path(),
                doc.encryption_method,
                user_attrs
            )
            
            actual = decrypted_path is not None
            result = "SUCCESS" if actual == expected else "FAILURE"
            
            test_results.append([
                user.username,
                doc.original_filename,
                "Yes" if actual else "No",
                "Yes" if expected else "No",
                result
            ])
        
        print("\n=== TEST RESULTS ===")
        print(tabulate(test_results, 
              headers=["User", "Document", "Access Granted", "Expected Access", "Test Result"]))
        
        # Demonstrate changing user attributes to grant access
        print("\n=== DEMONSTRATING ATTRIBUTE-BASED ACCESS CONTROL ===")
        
        # Tìm document liên quan đến Government
        gov_doc = None
        for doc in documents:
            if "Government" in doc.original_filename:
                gov_doc = doc
                break
        
        if gov_doc and david:
            print(f"\nInitially, David cannot access '{gov_doc.original_filename}'")
            print(f"Access policy: {gov_doc.access_policy}")
            print(f"David's attributes: {', '.join([f'{a.name}@{a.authority_name}' for a in david.attributes])}")
            
            # Thêm attribute "Director@Government" cho David
            director_attr = Attribute.query.filter_by(
                name='Director', 
                authority_name='Government'
            ).first()
            
            if director_attr:
                print("\nAdding 'Director@Government' attribute to David...")
                
                # Dùng quan hệ many-to-many để thêm
                david.attributes.append(director_attr)
                db.session.commit()
                
                # Sinh lại khóa ABE cho David với attribute mới
                encryption_service.generate_user_keys(
                    str(david.id),
                    'Government',
                    ['Director', 'Officer', 'Citizen']
                )
                
                # Thu thập lại attributes mới cho David
                user_attrs = []
                for a in david.attributes:
                    user_attrs.append(a)
                
                # Thử giải mã lại document
                decrypted_path = encryption_service.decrypt_document(
                    gov_doc.get_file_path(),
                    gov_doc.encryption_method,
                    user_attrs
                )
                
                if decrypted_path:
                    print(f"Success! David can now access the document!")
                    print(f"Decrypted file: {os.path.basename(decrypted_path)}")
                    
                    # Đọc nội dung của file đã giải mã
                    with open(decrypted_path, 'r') as f:
                        content = f.read()
                    
                    print(f"\nDecrypted content:\n{content}")
                else:
                    print("Access still denied. Something went wrong with the attribute update.")


if __name__ == "__main__":
    # Hãy chắc chắn đã chạy demo_setup.py trước khi chạy demo này
    run_demo()
