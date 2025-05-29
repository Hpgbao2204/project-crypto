"""
User model for the web application.
"""

# src/models/user.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from src.extensions import db  # Import từ extensions thay vì main

# Association table for user attributes
user_attributes = db.Table('user_attributes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('attribute_id', db.Integer, db.ForeignKey('attribute.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """User model for authentication and attribute-based access control."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(20), default='reader')  # 'data_owner', 'reader', 'authority'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # RSA keys for digital signatures
    public_key = db.Column(db.Text)
    private_key_encrypted = db.Column(db.Text)
    
    # Relationship with documents - explicitly specify foreign_keys to avoid ambiguity
    documents = db.relationship('Document', foreign_keys='Document.user_id', backref='owner', lazy='dynamic')
    
    # Relationship with attributes - fixed relationship
    attributes = db.relationship('Attribute', secondary=user_attributes, 
                                backref=db.backref('users', lazy='dynamic'))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password, password)
    
    def add_attribute(self, name, authority_name):
        """Add an attribute to the user."""
        attr = Attribute.query.filter_by(name=name, authority_name=authority_name).first()
        if not attr:
            attr = Attribute(name=name, authority_name=authority_name)
            db.session.add(attr)
        
        if attr not in self.attributes:
            self.attributes.append(attr)
    
    def has_attribute(self, attribute_name, authority_name):
        """Check if user has a specific attribute from an authority."""
        for attr in self.attributes:
            if attr.name == attribute_name and attr.authority_name == authority_name:
                return True
        return False
    
    def get_attributes_list(self):
        """Get list of user attributes in format 'attribute@authority'."""
        return [f"{attr.name}@{attr.authority_name}" for attr in self.attributes]
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'attributes': self.get_attributes_list(),
            'has_signature_keys': bool(self.public_key and self.private_key_encrypted)
        }

class Attribute(db.Model):
    """Attribute model for attribute-based access control."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    authority_name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(256))
    
    __table_args__ = (db.UniqueConstraint('name', 'authority_name', name='_name_authority_uc'),)
    
    def __repr__(self):
        return f'<Attribute {self.name}@{self.authority_name}>'
    
    def to_dict(self):
        """Convert attribute to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'authority_name': self.authority_name,
            'description': self.description,
            'full_name': f"{self.name}@{self.authority_name}"
        }
