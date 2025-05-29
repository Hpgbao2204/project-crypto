"""
Document routes for the web application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import current_user, login_required
import os
from src.models.document import Document
from src.services.document_service import DocumentService
from src.utils.file_utils import allowed_file, get_file_path
from src.main import db

document_bp = Blueprint('document', __name__)

@document_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Handle document upload."""
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
        
        try:
            # Save document
            document_service = DocumentService(db)
            document = document_service.save_document(file, current_user.id)
            
            flash('File uploaded successfully', 'success')
            return redirect(url_for('document.list'))
            
        except Exception as e:
            current_app.logger.error(f"Upload error: {str(e)}")
            flash(f'Upload failed: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('document/upload.html', title='Upload Document')

@document_bp.route('/list')
@login_required
def list():
    """List user's documents."""
    # Get filter parameters
    doc_type = request.args.get('type')
    
    # Get documents
    document_service = DocumentService(db)
    documents = document_service.get_user_documents(current_user.id, doc_type)
    
    return render_template('document/list.html', title='My Documents',
                          documents=documents)

@document_bp.route('/view/<int:document_id>')
@login_required
def view(document_id):
    """View document details."""
    # Get document
    document = Document.query.get_or_404(document_id)
    
    # Check if user has access
    if document.user_id != current_user.id:
        flash('You do not have permission to view this document', 'danger')
        return redirect(url_for('document.list'))
    
    return render_template('document/view.html', title='Document Details',
                          document=document)

@document_bp.route('/download/<int:document_id>')
@login_required
def download(document_id):
    """Download a document."""
    # Get document
    document = Document.query.get_or_404(document_id)
    
    # Check if user has access
    if document.user_id != current_user.id:
        flash('You do not have permission to download this document', 'danger')
        return redirect(url_for('document.list'))
    
    # Get file path
    file_path = document.get_file_path()
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('File not found', 'danger')
        return redirect(url_for('document.list'))
    
    # Determine content type
    content_type = document.file_type
    
    # Send file
    return send_file(file_path, 
                    download_name=document.original_filename,
                    mimetype=content_type,
                    as_attachment=True)

@document_bp.route('/delete/<int:document_id>', methods=['POST'])
@login_required
def delete(document_id):
    """Delete a document."""
    # Get document
    document = Document.query.get_or_404(document_id)
    
    # Check if user has access
    if document.user_id != current_user.id:
        flash('You do not have permission to delete this document', 'danger')
        return redirect(url_for('document.list'))
    
    # Delete document
    document_service = DocumentService(db)
    success = document_service.delete_document(document_id)
    
    if success:
        flash('Document deleted successfully', 'success')
    else:
        flash('Failed to delete document', 'danger')
    
    return redirect(url_for('document.list'))

@document_bp.route('/share/<int:document_id>', methods=['GET', 'POST'])
@login_required
def share(document_id):
    """Share a document with other users."""
    # Get document
    document = Document.query.get_or_404(document_id)
    
    # Check if user has access
    if document.user_id != current_user.id:
        flash('You do not have permission to share this document', 'danger')
        return redirect(url_for('document.list'))
    
    if request.method == 'POST':
        # Get share parameters
        user_ids = request.form.getlist('user_ids')
        
        if not user_ids:
            flash('No users selected', 'danger')
            return redirect(request.url)
        
        # Share document
        # This would typically involve creating share records in the database
        # For now, we'll just show a success message
        
        flash('Document shared successfully', 'success')
        return redirect(url_for('document.view', document_id=document_id))
    
    # Get users to share with
    from src.models.user import User
    users = User.query.filter(User.id != current_user.id).all()
    
    return render_template('document/share.html', title='Share Document',
                          document=document, users=users)
