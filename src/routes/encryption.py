"""
Encryption routes for the web application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
import json
from src.models.document import Document
from src.services.document_service import DocumentService
from src.services.encryption_service import EncryptionService
from src.utils.file_utils import allowed_file, get_file_path
from src.extensions import db

encryption_bp = Blueprint('encryption', __name__)

@encryption_bp.route('/encrypt', methods=['GET', 'POST'])
@login_required
def encrypt():
    """Handle file encryption."""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('File type not allowed', 'danger')
            return redirect(request.url)
        
        # Get encryption parameters
        encryption_method = request.form.get('encryption_method', 'hybrid')
        access_policy = request.form.get('access_policy')
        
        if not access_policy:
            flash('Access policy is required', 'danger')
            return redirect(request.url)
        
        try:
            # Save original document
            document_service = DocumentService(db)
            document = document_service.save_document(file, current_user.id)
            
            # Encrypt document
            encryption_service = EncryptionService()
            
            encrypted_path, metadata = encryption_service.encrypt_file(
                document.get_file_path(), 
                access_policy, 
                str(current_user.id)
            )
            
            # Save encrypted document
            encrypted_document = document_service.save_encrypted_document(
                document.id,
                os.path.basename(encrypted_path),
                encryption_method,
                access_policy,
                current_user.id
            )
            
            flash('File encrypted successfully', 'success')
            return redirect(url_for('document.list'))
            
        except Exception as e:
            current_app.logger.error(f"Encryption error: {str(e)}")
            flash(f'Encryption failed: {str(e)}', 'danger')
            return redirect(request.url)
    
    # Get user's attributes for policy guidance
    user_attributes = []
    if current_user.attributes:
        user_attributes = [f"{attr.name}@{attr.authority_name}" for attr in current_user.attributes]
    
    return render_template('encryption/encrypt.html', title='Encrypt Document',
                          user_attributes=user_attributes)

@encryption_bp.route('/decrypt/<int:document_id>', methods=['GET', 'POST'])
@login_required
def decrypt(document_id):
    """Handle file decryption."""
    # Get document
    document = Document.query.get_or_404(document_id)
    
    # Check if document is encrypted
    if document.doc_type != 'encrypted':
        flash('Document is not encrypted', 'danger')
        return redirect(url_for('document.list'))
    
    if request.method == 'POST':
        try:
            # Decrypt document
            encryption_service = EncryptionService()
            
            decrypted_path, success = encryption_service.decrypt_file(
                document.get_file_path(),
                str(current_user.id)
            )
            
            if not success:
                flash('Decryption failed: Your attributes do not satisfy the access policy', 'danger')
                return redirect(url_for('document.list'))
            
            # Save decrypted document
            document_service = DocumentService(db)
            
            # Create a temporary file object from the decrypted file
            from werkzeug.datastructures import FileStorage
            with open(decrypted_path, 'rb') as f:
                file = FileStorage(
                    stream=f,
                    filename=document.original_filename.replace('.encrypted', ''),
                    content_type=document.file_type
                )
                
                decrypted_document = document_service.save_document(
                    file, 
                    current_user.id,
                    doc_type='original'
                )
            
            flash('File decrypted successfully', 'success')
            return redirect(url_for('document.view', document_id=decrypted_document.id))
            
        except Exception as e:
            current_app.logger.error(f"Decryption error: {str(e)}")
            flash(f'Decryption failed: {str(e)}', 'danger')
            return redirect(url_for('document.list'))
    
    return render_template('encryption/decrypt.html', title='Decrypt Document',
                          document=document)

@encryption_bp.route('/policy-editor', methods=['GET'])
@login_required
def policy_editor():
    """Policy editor helper."""
    # Get all attributes from the system
    from src.models.user import Attribute
    attributes = Attribute.query.all()
    
    # Group attributes by authority
    authorities = {}
    for attr in attributes:
        if attr.authority_name not in authorities:
            authorities[attr.authority_name] = []
        authorities[attr.authority_name].append(attr.name)
    
    return render_template('encryption/policy_editor.html', title='Policy Editor',
                          authorities=authorities)
