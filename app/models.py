from datetime import datetime
import string
import random
from flask import url_for
from app import db, bcrypt

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(256), nullable=True)
    
    # Relationship
    urls = db.relationship('ShortURL', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_verified": self.is_verified,
            "profile_picture": self.profile_picture,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def create_from_google(cls, google_data):
        return cls(
            email=google_data['email'],
            username=google_data.get('name', google_data['email'].split('@')[0]),
            google_id=google_data['sub'],
            is_verified=True,
            profile_picture=google_data.get('picture')
        )

    def __repr__(self):
        return f'<User {self.email}>'

class ShortURL(db.Model):
    __tablename__ = 'short_url'
    
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512), nullable=False)
    short_code = db.Column(db.String(6), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    access_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(200), nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.short_code:
            self.short_code = self._generate_unique_short_code()

    def _generate_unique_short_code(self):
        short_code = generate_short_code()
        while ShortURL.query.filter_by(short_code=short_code).first() is not None:
            short_code = generate_short_code()
        return short_code

    def to_dict(self):
        return {
            "id": self.id,
            "original_url": self.original_url,
            "short_code": self.short_code,
            "short_url": url_for('api.get_original_url', 
                                short_code=self.short_code, 
                                _external=True),
            "user_id": self.user_id,
            "access_count": self.access_count,
            "title": self.title,
            "tags": self.tags.split(',') if self.tags else [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner": self.owner.to_dict() if self.owner else None
        }

    def increment_access_count(self):
        self.access_count += 1
        db.session.commit()

    def __repr__(self):
        return f'<ShortURL {self.short_code}>'