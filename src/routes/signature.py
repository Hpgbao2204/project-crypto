"""
Signature routes for the web application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import current_user, login_required
import os
from src.models.document import Document
from src.models.user import User
from src.services.document_service import DocumentService
from src.services.signature_service import SignatureService
from src.utils.file_utils import allowed_file, get_file_path
from src.extensions import db

signature_bp = Blueprint('signature', __name__)

@signature_bp.route('/sign/<int:document_id>', methods=['GET', 'POST'])
@login_required
def sign(document_id):
    """Sign a document."""
    # Get document
    document = Document.query.get_or_404(document_id)
    
    # Check if user has access
    if document.user_id != current_user.id:
        flash('You do not have permission to sign this document', 'danger')
        return redirect(url_for('document.list'))
    
    # Check if document is already signed
    if document.is_signed:
        flash('Document is already signed', 'warning')
        return redirect(url_for('document.view', document_id=document_id))
    
    if request.method == 'POST':
        # Get password for private key
        password = request.form.get('password')
        
        if not password:
            flash('Password is required', 'danger')
            return redirect(request.url)
        
        try:
            # Sign document
            signature_service = SignatureService()
            
            signature_path, metadata = signature_service.sign_document(
                document.get_file_path(),
                str(current_user.id),
                password,
                current_user.private_key_encrypted
            )
            
            if not signature_path:
                flash('Signing failed: Invalid password or key error', 'danger')
                return redirect(request.url)
            
            # Update document
            document_service = DocumentService(db)
            signed_document = document_service.save_signed_document(
                document.id,
                os.path.basename(signature_path),
                current_user.id
            )
            
            flash('Document signed successfully', 'success')
            return redirect(url_for('document.view', document_id=document_id))
            
        except Exception as e:
            current_app.logger.error(f"Signing error: {str(e)}")
            flash(f'Signing failed: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('signature/sign.html', title='Sign Document',
                          document=document)

@signature_bp.route('/verify/<int:document_id>', methods=['GET', 'POST'])
@login_required
def verify(document_id):
    """Verify a document's signature."""
    # Get document
    document = Document.query.get_or_404(document_id)
    
    # Check if document is signed
    if not document.is_signed:
        flash('Document is not signed', 'danger')
        return redirect(url_for('document.list'))
    
    # Get signer
    signer = User.query.get(document.signer_id)
    
    if not signer:
        flash('Signer not found', 'danger')
        return redirect(url_for('document.view', document_id=document_id))
    
    if request.method == 'POST':
        try:
            # Verify signature
            signature_service = SignatureService()
            
            is_valid = signature_service.verify_signature(
                document.get_file_path(),
                document.get_signature_path(),
                signer.public_key
            )
            
            if is_valid:
                flash('Signature is valid', 'success')
            else:
                flash('Signature is invalid', 'danger')
            
            return redirect(url_for('document.view', document_id=document_id))
            
        except Exception as e:
            current_app.logger.error(f"Verification error: {str(e)}")
            flash(f'Verification failed: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('signature/verify.html', title='Verify Signature',
                          document=document, signer=signer)

@signature_bp.route('/download-signature/<int:document_id>')
@login_required
def download_signature(document_id):
    """Download a document's signature."""
    # Get document
    document = Document.query.get_or_404(document_id)
    
    # Check if document is signed
    if not document.is_signed:
        flash('Document is not signed', 'danger')
        return redirect(url_for('document.list'))
    
    # Get signature path
    signature_path = document.get_signature_path()
    
    # Check if signature exists
    if not signature_path or not os.path.exists(signature_path):
        flash('Signature file not found', 'danger')
        return redirect(url_for('document.view', document_id=document_id))
    
    # Send file
    return send_file(signature_path, 
                    download_name=f"{document.original_filename}.sig",
                    mimetype='application/octet-stream',
                    as_attachment=True)

@signature_bp.route('/keys', methods=['GET', 'POST'])
@login_required
def manage_keys():
    """Manage signature keys."""
    if request.method == 'POST':
        # Get password
        password = request.form.get('password')
        
        if not password:
            flash('Password is required', 'danger')
            return redirect(request.url)
        
        try:
            # Generate new key pair
            signature_service = SignatureService()
            
            public_key, encrypted_private_key = signature_service.generate_key_pair(
                str(current_user.id),
                password
            )
            
            # Update user
            current_user.public_key = public_key
            current_user.private_key_encrypted = encrypted_private_key
            
            db.session.commit()
            
            flash('Signature keys generated successfully', 'success')
            return redirect(url_for('signature.manage_keys'))
            
        except Exception as e:
            current_app.logger.error(f"Key generation error: {str(e)}")
            flash(f'Key generation failed: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('signature/keys.html', title='Manage Signature Keys')

@signature_bp.route('/export-public-key')
@login_required
def export_public_key():
    """Export user's public key."""
    if not current_user.public_key:
        flash('No public key available', 'danger')
        return redirect(url_for('signature.manage_keys'))
    
    # Create a temporary file for the public key
    import tempfile
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pem')
    temp_file.write(current_user.public_key.encode('utf-8'))
    temp_file.close()
    
    # Send file
    return send_file(temp_file.name, 
                    download_name=f"{current_user.username}_public_key.pem",
                    mimetype='application/x-pem-file',
                    as_attachment=True)
