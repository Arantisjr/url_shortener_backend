# auth.py
from flask import Blueprint, request, jsonify, url_for, session
from app.models import User
from app import db, bcrypt, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from app.utils import error_response
from authlib.integrations.flask_client import OAuth
from app.oauth import oauth, handle_google_auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return error_response(400, 'Email and password are required')
    
    # Make username optional (can be added later)
    username = data.get('username', data['email'].split('@')[0])
    
    if User.query.filter_by(email=data['email']).first():
        return error_response(400, 'Email already exists')
    
    if 'username' in data and User.query.filter_by(username=username).first():
        return error_response(400, 'Username already exists')
    
    user = User(
        username=username,
        email=data['email']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1))
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'Error creating user: {str(e)}')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return error_response(400, 'Email and password are required')
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return error_response(401, 'Invalid email or password')
    
    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(hours=1))
    
    return jsonify({
        'message': 'Logged in successfully',
        'access_token': access_token,
        'user': user.to_dict()
    })

@auth_bp.route('/google/login')
def google_login():
    """Initiate Google OAuth flow"""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        user = handle_google_auth()  # Use the function from oauth.py
        
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1))
        
        return jsonify({
            'message': 'Google authentication successful',
            'access_token': access_token,
            'user': user.to_dict()
        })
    except Exception as e:
        return error_response(401, f'Google authentication failed: {str(e)}')

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Example protected endpoint"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response(404, 'User not found')
    
    return jsonify({
        'message': 'This is a protected route',
        'user': user.to_dict()
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user's profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response(404, 'User not found')
    
    return jsonify(user.to_dict())