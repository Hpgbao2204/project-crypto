"""
Authentication routes for the web application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# Fix for Werkzeug import error - use urllib.parse instead of werkzeug.urls
from urllib.parse import urlparse, urljoin
from src.models.user import User
from src.encryption.digital_signature import DigitalSignature
from src.main import db

auth_bp = Blueprint('auth', __name__)

# Helper function to check if URL is safe for redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        if not next_page or not is_safe_url(next_page):
            next_page = url_for('index')
        
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        # Validate input
        if not username or not email or not password or not confirm_password:
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role
        )
        
        # Add attributes
        for key, value in request.form.items():
            if key.startswith('attribute_') and value == '1':
                attr_name = key.replace('attribute_', '')
                authority_name = request.form.get(f'authority_{attr_name}')
                if authority_name:
                    new_user.add_attribute(attr_name, authority_name)
        
        # Generate signature keys
        try:
            signature = DigitalSignature()
            public_key, private_key_encrypted = signature.generate_key_pair(
                username,  # Use username as identifier
                password   # Use password to encrypt private key
            )
            
            new_user.public_key = public_key
            new_user.private_key_encrypted = private_key_encrypted
            
        except Exception as e:
            current_app.logger.error(f"Key generation error: {str(e)}")
            flash('Error generating signature keys', 'danger')
            return redirect(url_for('auth.register'))
        
        # Save user to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    # Get available authorities and attributes for the form
    authorities = {
        'Hospital': ['Doctor', 'Nurse', 'Admin', 'Researcher']
    }
    
    return render_template('auth/register.html', title='Register',
                          authorities=authorities)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile."""
    return render_template('auth/profile.html', title='My Profile')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Check current password
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Update password
        current_user.password = generate_password_hash(new_password)
        
        # Re-encrypt private key with new password
        if current_user.private_key_encrypted:
            try:
                signature = DigitalSignature()
                
                # First decrypt with old password
                private_key = signature.decrypt_private_key(
                    current_user.private_key_encrypted,
                    current_password
                )
                
                # Then re-encrypt with new password
                current_user.private_key_encrypted = signature.encrypt_private_key(
                    private_key,
                    new_password
                )
                
            except Exception as e:
                current_app.logger.error(f"Key re-encryption error: {str(e)}")
                flash('Error re-encrypting signature keys', 'danger')
                return redirect(url_for('auth.change_password'))
        
        db.session.commit()
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', title='Change Password')
