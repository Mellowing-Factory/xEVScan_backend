from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from models import User
from extensions import db
from utils import send_verification_email, validate_required_fields, create_error_response, create_success_response
import secrets

# Create namespace
auth_ns = Namespace('auth', description='Authentication operations')

@auth_ns.route('/register')
class AuthRegister(Resource):
    @auth_ns.expect(auth_ns.models['auth_register'])
    @auth_ns.marshal_with(auth_ns.models['success_response'], code=201)
    @auth_ns.response(400, 'Validation Error', auth_ns.models['error_response'])
    @auth_ns.response(409, 'Email Already Registered', auth_ns.models['error_response'])
    @auth_ns.response(500, 'Internal Server Error', auth_ns.models['error_response'])
    def post(self):
        """Register a new user account"""
        try:
            data = request.get_json()
            
            # Validate required fields
            is_valid, error_message = validate_required_fields(data, ['email', 'password', 'name'])
            if not is_valid:
                return create_error_response(error_message), 400
            
            # Check if user already exists
            if User.query.filter_by(email=data['email'].lower()).first():
                return create_error_response('Email already registered'), 409
            
            # Create new user
            user = User(
                email=data['email'].lower(),
                name=data['name'],
                verification_token=secrets.token_urlsafe(32)
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            send_verification_email(user.email, user.verification_token)
            
            return {
                'message': 'User registered successfully. Please check your email for verification.',
                'user_id': user.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return create_error_response(str(e)), 500

@auth_ns.route('/login')
class AuthLogin(Resource):
    @auth_ns.expect(auth_ns.models['auth_login'])
    @auth_ns.marshal_with(auth_ns.models['auth_response'])
    @auth_ns.response(400, 'Validation Error', auth_ns.models['error_response'])
    @auth_ns.response(401, 'Invalid Credentials', auth_ns.models['error_response'])
    @auth_ns.response(500, 'Internal Server Error', auth_ns.models['error_response'])
    def post(self):
        """Login user and return JWT token"""
        try:
            data = request.get_json()
            
            # Validate required fields
            is_valid, error_message = validate_required_fields(data, ['email', 'password'])
            if not is_valid:
                return create_error_response(error_message), 400
            
            user = User.query.filter_by(email=data['email'].lower()).first()
            
            if not user or not user.check_password(data['password']):
                return create_error_response('Invalid credentials'), 401
            
            if not user.is_verified:
                return create_error_response('Please verify your email first'), 401
            
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            return {
                'access_token': access_token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            return create_error_response(str(e)), 500

@auth_ns.route('/verify/<string:token>')
class AuthVerify(Resource):
    @auth_ns.marshal_with(auth_ns.models['success_response'])
    @auth_ns.response(400, 'Invalid Token', auth_ns.models['error_response'])
    @auth_ns.response(500, 'Internal Server Error', auth_ns.models['error_response'])
    def get(self, token):
        """Verify user email with verification token"""
        try:
            user = User.query.filter_by(verification_token=token).first()
            
            if not user:
                return create_error_response('Invalid verification token'), 400
            
            user.is_verified = True
            user.verification_token = None
            db.session.commit()
            
            return {'message': 'Email verified successfully'}
            
        except Exception as e:
            db.session.rollback()
            return create_error_response(str(e)), 500