"""
Document model for the web application.
"""

from datetime import datetime
import os
from src.extensions import db

class Document(db.Model):
    """Document model for storing file information."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    file_type = db.Column(db.String(64))
    file_size = db.Column(db.Integer)  # Size in bytes
    
    # Document type and status
    doc_type = db.Column(db.String(20))  # 'original', 'encrypted', 'signed'
    encryption_method = db.Column(db.String(20), nullable=True)  # 'maabe', 'hybrid', None
    access_policy = db.Column(db.Text, nullable=True)
    
    # Signature information
    is_signed = db.Column(db.Boolean, default=False)
    signature_file = db.Column(db.String(256), nullable=True)
    signer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=True)
    
    # Define relationship with explicit foreign keys to avoid ambiguity
    # This relationship is for documents that are children of other documents
    children = db.relationship('Document', 
                              backref=db.backref('parent', remote_side=[id]),
                              foreign_keys=[parent_id])
    
    # Define relationship with signer with explicit foreign keys
    signer = db.relationship('User', foreign_keys=[signer_id], backref='signed_documents')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'
    
    def get_file_path(self):
        """Get the full path to the document file."""
        from src.main import app
        return os.path.join(app.config['UPLOAD_FOLDER'], self.filename)
    
    def get_signature_path(self):
        """Get the full path to the signature file if it exists."""
        if not self.signature_file:
            return None
        from src.main import app
        return os.path.join(app.config['UPLOAD_FOLDER'], self.signature_file)
    
    def to_dict(self):
        """Convert document to dictionary."""
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'doc_type': self.doc_type,
            'encryption_method': self.encryption_method,
            'access_policy': self.access_policy,
            'is_signed': self.is_signed,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
