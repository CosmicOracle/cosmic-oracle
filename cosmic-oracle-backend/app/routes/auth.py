from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

# Change 'bp' to 'auth_bp' to match how it's imported in app/routes/__init__.py
auth_bp = Blueprint('auth', __name__) # Added url_prefix='/auth' for consistency with common Flask app structures

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing email or password"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already registered"}), 400

    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing email or password"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=7)) # Token expires in 7 days
        return jsonify(access_token=access_token, user_id=user.id, email=user.email), 200
    
    return jsonify({"msg": "Invalid email or password"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    birth_data_info = None
    if user.birth_data:
        birth_data_info = {
            "birth_date": user.birth_data.birth_date.isoformat() if user.birth_data.birth_date else None,
            "birth_time": user.birth_data.birth_time.isoformat() if user.birth_data.birth_time else None,
            "birth_location_name": user.birth_data.birth_location_name,
            "latitude": user.birth_data.latitude,
            "longitude": user.birth_data.longitude,
            "timezone_str": user.birth_data.timezone_str,
            "sun_sign": user.birth_data.sun_sign,
            "moon_sign": user.birth_data.moon_sign,
            "rising_sign": user.birth_data.rising_sign
        }

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "birth_data": birth_data_info
    }), 200
