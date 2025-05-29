"""
Document service for the web application.
"""

import os
import json
from datetime import datetime
from flask import current_app
from src.models.document import Document
from src.utils.file_utils import save_uploaded_file, get_file_path, delete_file

class DocumentService:
    """Service for handling document operations."""
    
    def __init__(self, db):
        """
        Initialize the document service.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def save_document(self, file, user_id, doc_type='original'):
        """
        Save a document to the system.
        
        Args:
            file: File object from request.files
            user_id (int): ID of the document owner
            doc_type (str): Type of document ('original', 'encrypted', 'signed')
            
        Returns:
            Document: Saved document object
        """
        # Save the file
        filename, original_filename, file_type, file_size = save_uploaded_file(file)
        
        # Create document record
        document = Document(
            filename=filename,
            original_filename=original_filename,
            file_type=file_type,
            file_size=file_size,
            doc_type=doc_type,
            user_id=user_id
        )
        
        # Save to database
        self.db.session.add(document)
        self.db.session.commit()
        
        return document
    
    def get_document(self, document_id):
        """
        Get a document by ID.
        
        Args:
            document_id (int): Document ID
            
        Returns:
            Document: Document object or None
        """
        return Document.query.get(document_id)
    
    def get_user_documents(self, user_id, doc_type=None):
        """
        Get documents for a user.
        
        Args:
            user_id (int): User ID
            doc_type (str): Optional filter by document type
            
        Returns:
            list: List of Document objects
        """
        query = Document.query.filter_by(user_id=user_id)
        
        if doc_type:
            query = query.filter_by(doc_type=doc_type)
        
        return query.order_by(Document.created_at.desc()).all()
    
    def delete_document(self, document_id):
        """
        Delete a document.
        
        Args:
            document_id (int): Document ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        document = self.get_document(document_id)
        
        if not document:
            return False
        
        try:
            # Delete the file
            delete_file(document.filename)
            
            # Delete signature file if exists
            if document.signature_file:
                delete_file(document.signature_file)
            
            # Delete from database
            self.db.session.delete(document)
            self.db.session.commit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error deleting document: {str(e)}")
            self.db.session.rollback()
            return False
    
    def save_encrypted_document(self, original_document_id, encrypted_filename, encryption_method, access_policy, user_id):
        """
        Save an encrypted document.
        
        Args:
            original_document_id (int): ID of the original document
            encrypted_filename (str): Filename of the encrypted document
            encryption_method (str): Encryption method used ('maabe', 'hybrid')
            access_policy (str): Access policy string
            user_id (int): User ID
            
        Returns:
            Document: Encrypted document object
        """
        # Get original document
        original_document = self.get_document(original_document_id)
        
        if not original_document:
            return None
        
        # Get file info
        file_path = get_file_path(encrypted_filename)
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document = Document(
            filename=encrypted_filename,
            original_filename=f"{original_document.original_filename}.encrypted",
            file_type="application/json",
            file_size=file_size,
            doc_type="encrypted",
            encryption_method=encryption_method,
            access_policy=access_policy,
            user_id=user_id,
            parent_id=original_document_id
        )
        
        # Save to database
        self.db.session.add(document)
        self.db.session.commit()
        
        return document
    
    def save_signed_document(self, original_document_id, signature_filename, signer_id):
        """
        Save a signed document.
        
        Args:
            original_document_id (int): ID of the original document
            signature_filename (str): Filename of the signature file
            signer_id (int): ID of the signer
            
        Returns:
            Document: Updated document object
        """
        # Get original document
        document = self.get_document(original_document_id)
        
        if not document:
            return None
        
        # Update document record
        document.is_signed = True
        document.signature_file = signature_filename
        document.signer_id = signer_id
        document.doc_type = "signed"
        document.updated_at = datetime.utcnow()
        
        # Save to database
        self.db.session.commit()
        
        return document
