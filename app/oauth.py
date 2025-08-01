from flask import redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from .models import User  # Changed from 'from app.models'
from . import db  # Changed from 'from app import db'

oauth = OAuth()

def init_oauth(app):
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    return oauth

def handle_google_auth():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    
    # Extract user data from Google
    email = user_info['email']
    name = user_info.get('name', email.split('@')[0])
    google_id = user_info['sub']
    
    # Find or create user
    user = User.query.filter_by(email=email).first()
    
    if not user:
        user = User(
            username=name,
            email=email,
            google_id=google_id,
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()
    
    return user