"""
File utility functions for the web application.
"""

import os
import uuid
import json
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename, allowed_extensions=None):
    """
    Check if a file has an allowed extension.
    
    Args:
        filename (str): The filename to check
        allowed_extensions (set): Set of allowed extensions, defaults to PDF, TXT, DOC, DOCX
        
    Returns:
        bool: True if file is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'txt', 'doc', 'docx'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, directory=None):
    """
    Save an uploaded file with a secure filename.
    
    Args:
        file: The file object from request.files
        directory (str): Directory to save the file, defaults to app's UPLOAD_FOLDER
        
    Returns:
        tuple: (saved_filename, original_filename, file_type, file_size)
    """
    if directory is None:
        directory = current_app.config['UPLOAD_FOLDER']
    
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Get original filename and secure it
    original_filename = file.filename
    file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(directory, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    # Get file info
    file_size = os.path.getsize(file_path)
    file_type = file.content_type or f"application/{file_extension}"
    
    return unique_filename, original_filename, file_type, file_size

def get_file_path(filename, directory=None):
    """
    Get the full path to a file.
    
    Args:
        filename (str): The filename
        directory (str): Directory containing the file, defaults to app's UPLOAD_FOLDER
        
    Returns:
        str: Full path to the file
    """
    if directory is None:
        directory = current_app.config['UPLOAD_FOLDER']
    
    return os.path.join(directory, filename)

def delete_file(filename, directory=None):
    """
    Delete a file.
    
    Args:
        filename (str): The filename to delete
        directory (str): Directory containing the file, defaults to app's UPLOAD_FOLDER
        
    Returns:
        bool: True if file was deleted, False otherwise
    """
    if directory is None:
        directory = current_app.config['UPLOAD_FOLDER']
    
    file_path = os.path.join(directory, filename)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def save_json_data(data, filename, directory=None):
    """
    Save data as JSON file.
    
    Args:
        data (dict): Data to save
        filename (str): Filename for the JSON file
        directory (str): Directory to save the file, defaults to app's UPLOAD_FOLDER
        
    Returns:
        str: Full path to the saved file
    """
    if directory is None:
        directory = current_app.config['UPLOAD_FOLDER']
    
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Create full path
    file_path = os.path.join(directory, filename)
    
    # Save data as JSON
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return file_path

def load_json_data(filename, directory=None):
    """
    Load data from JSON file.
    
    Args:
        filename (str): Filename of the JSON file
        directory (str): Directory containing the file, defaults to app's UPLOAD_FOLDER
        
    Returns:
        dict: Loaded data, or None if file doesn't exist
    """
    if directory is None:
        directory = current_app.config['UPLOAD_FOLDER']
    
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception:
        return None
