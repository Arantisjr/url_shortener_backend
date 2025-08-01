from flask import Blueprint, request, jsonify, redirect, current_app
from app.models import ShortURL
from app.utils import validate_url, error_response, generate_short_code
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from datetime import datetime
import validators

bp = Blueprint('api', __name__)

@bp.route('/shorten', methods=['POST'])
@jwt_required()
def create_short_url():
    """
    Create a new short URL
    ---
    tags:
      - URL Shortener
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            url:
              type: string
              example: https://example.com/very/long/url
            shortCode:
              type: string
              example: mylink
    responses:
      201:
        description: Short URL created
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or 'url' not in data:
        return error_response(400, 'URL is required')
    
    original_url = data['url']
    
    if not validators.url(original_url):
        return error_response(400, 'Invalid URL format')
    
    # Process short code
    short_code = data.get('shortCode')
    
    if short_code:
        if len(short_code) < 3 or len(short_code) > 8:
            return error_response(400, 'Short code must be between 3 and 8 characters')
        
        if not short_code.isalnum():
            return error_response(400, 'Short code can only contain letters and numbers')
        
        if ShortURL.query.filter_by(short_code=short_code).first():
            return error_response(400, 'Short code already in use')
    else:
        short_code = generate_short_code(4)  # Default length
    
    # Create and save short URL
    short_url = ShortURL(
        original_url=original_url,
        short_code=short_code,
        user_id=current_user_id
    )
    
    try:
        db.session.add(short_url)
        db.session.commit()
        return jsonify({
            'id': short_url.id,
            'original_url': short_url.original_url,
            'short_code': short_url.short_code,
            'short_url': f"{current_app.config['SHORT_DOMAIN']}/{short_url.short_code}",
            'access_count': short_url.access_count,
            'created_at': short_url.created_at.isoformat(),
            'user_id': short_url.user_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'Error creating short URL: {str(e)}')

@bp.route('/<short_code>', methods=['GET'])
def redirect_short_url(short_code):
    """
    Redirect to original URL
    ---
    tags:
      - URL Shortener
    parameters:
      - name: short_code
        in: path
        type: string
        required: true
    responses:
      302:
        description: Redirect to original URL
      404:
        description: Short URL not found
    """
    short_url = ShortURL.query.filter_by(short_code=short_code).first()
    
    if not short_url:
        return error_response(404, 'Short URL not found')
    
    try:
        short_url.access_count += 1
        short_url.last_accessed = datetime.utcnow()
        db.session.commit()
        return redirect(short_url.original_url, code=302)
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'Error redirecting: {str(e)}')

@bp.route('/api/url/<short_code>', methods=['GET'])
@jwt_required()
def get_url_details(short_code):
    """
    Get URL details (authenticated)
    ---
    tags:
      - URL Shortener
    security:
      - Bearer: []
    parameters:
      - name: short_code
        in: path
        type: string
        required: true
    responses:
      200:
        description: URL details
      404:
        description: URL not found
    """
    current_user_id = get_jwt_identity()
    short_url = ShortURL.query.filter_by(short_code=short_code, user_id=current_user_id).first()
    
    if not short_url:
        return error_response(404, 'Short URL not found or not owned by you')
    
    return jsonify(short_url.to_dict())

@bp.route('/api/url/<short_code>', methods=['PUT'])
@jwt_required()
def update_short_url(short_code):
    current_user_id = get_jwt_identity()
    short_url = ShortURL.query.filter_by(short_code=short_code, user_id=current_user_id).first()
    
    if not short_url:
        return error_response(404, 'Short URL not found or not owned by you')
    
    data = request.get_json()
    
    if not data or 'url' not in data:
        return error_response(400, 'URL is required')
    
    new_url = data['url']
    
    if not validators.url(new_url):
        return error_response(400, 'Invalid URL format')
    
    short_url.original_url = new_url
    short_url.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify(short_url.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'Error updating short URL: {str(e)}')

@bp.route('/api/url/<short_code>', methods=['DELETE'])
@jwt_required()
def delete_short_url(short_code):
    current_user_id = get_jwt_identity()
    short_url = ShortURL.query.filter_by(short_code=short_code, user_id=current_user_id).first()
    
    if not short_url:
        return error_response(404, 'Short URL not found or not owned by you')
    
    try:
        db.session.delete(short_url)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'Error deleting short URL: {str(e)}')

@bp.route('/api/user/urls', methods=['GET'])
@jwt_required()
def get_user_urls():
    current_user_id = get_jwt_identity()
    urls = ShortURL.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([url.to_dict() for url in urls])