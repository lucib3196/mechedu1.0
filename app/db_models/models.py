from typing import Any
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, RelationshipProperty
from flask import current_app

# Initialize SQLAlchemy
db = SQLAlchemy()


class EduModule(db.Model):
    __tablename__ = "edu_module"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    folders = db.relationship("Folder", backref="edu_module", lazy=True)

    def __repr__(self):
        return f"<EduModule {self.name}>"

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    files = db.relationship('File', backref='folder', lazy=True)
    module_id = db.Column(db.Integer, db.ForeignKey('edu_module.id'), nullable=False)

    def __repr__(self):
        return f"<Folder {self.name}>"


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    content = db.Column(db.String, nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)

    def __repr__(self):
        return f"<File {self.filename} in folder {self.folder_id}>"


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # Retrieve the admin email(s) from the config
            admin_email = current_app.config.get('FLASKY_ADMIN')
            
            # Check if admin_email is a string or list
            if isinstance(admin_email, str):
                # If it's a single email or a comma-separated string, split it into a list
                admin_email = [email.strip() for email in admin_email.split(',')]
            
            print(f"Debug: self.email={self.email}, admin_email={admin_email}")
            
            # Check if the current user's email is in the list of admin emails
            if self.email in admin_email:
                self.role = Role.query.filter_by(name='Administrator').first()
                print(f"Debug: Assigned Administrator role: {self.role}")
            
            # Assign the default role if no specific role was found
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
                print(f"Debug: Assigned default role: {self.role}")



    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
class Permission:
    PRACTICE = 1
    GENERATE = 2
    MODIFY = 4
    ADMIN = 8    
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer, default=0)  # Ensure permissions is initialized to 0
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm
    
    @staticmethod
    def insert_roles():
        roles = {
            'Student': [Permission.PRACTICE],
            'Reviewer': [Permission.PRACTICE, Permission.GENERATE, Permission.MODIFY],
            'Administrator': [Permission.PRACTICE, Permission.GENERATE, Permission.MODIFY, Permission.ADMIN]
        }
        default_role = 'Student'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


