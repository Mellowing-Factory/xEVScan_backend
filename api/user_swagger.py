from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, UserDeviceMapping
from extensions import db
from utils import validate_required_fields, create_error_response, create_success_response

# Create namespace
user_ns = Namespace('user', description='User management operations')

@user_ns.route('/profile')
class UserProfile(Resource):
    @user_ns.doc('get_user_profile')
    @user_ns.doc(security='Bearer')
    @jwt_required()
    @user_ns.response(200, 'Success')
    @user_ns.response(404, 'User Not Found', user_ns.models['error_response'])
    @user_ns.response(401, 'Authentication Required', user_ns.models['error_response'])
    def get(self):
        """Get current user profile information"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return create_error_response('User not found'), 404
            
            return user.to_dict()
            
        except Exception as e:
            return create_error_response(str(e)), 500

@user_ns.route('/devices')
class UserDevices(Resource):
    @user_ns.doc('get_user_devices')
    @user_ns.doc(security='Bearer')
    @jwt_required()
    @user_ns.response(200, 'Success', [user_ns.models['device_response']])
    @user_ns.response(401, 'Authentication Required', user_ns.models['error_response'])
    def get(self):
        """Get all devices linked to current user"""
        try:
            user_id = get_jwt_identity()
            mappings = UserDeviceMapping.query.filter_by(user_id=user_id).all()
            
            devices = [{
                'device_id': mapping.device_id,
                'device_name': mapping.device_name,
                'created_at': mapping.created_at.isoformat()
            } for mapping in mappings]
            
            return {'devices': devices}
            
        except Exception as e:
            return create_error_response(str(e)), 500
    
    @user_ns.doc('add_user_device')
    @user_ns.expect(user_ns.models['device_add'])
    @user_ns.marshal_with(user_ns.models['success_response'], code=201)
    @user_ns.doc(security='Bearer')
    @jwt_required()
    @user_ns.response(400, 'Validation Error', user_ns.models['error_response'])
    @user_ns.response(409, 'Device Already Linked', user_ns.models['error_response'])
    @user_ns.response(401, 'Authentication Required', user_ns.models['error_response'])
    def post(self):
        """Link a new device to current user"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Validate required fields
            is_valid, error_message = validate_required_fields(data, ['device_id'])
            if not is_valid:
                return create_error_response(error_message), 400
            
            # Check if mapping already exists
            existing = UserDeviceMapping.query.filter_by(
                user_id=user_id, 
                device_id=data['device_id']
            ).first()
            
            if existing:
                return create_error_response('Device already linked to this user'), 409
            
            # Create new mapping
            mapping = UserDeviceMapping(
                user_id=user_id,
                device_id=data['device_id'],
                device_name=data.get('device_name', data['device_id'])
            )
            
            db.session.add(mapping)
            db.session.commit()
            
            return {
                'message': 'Device linked successfully',
                'device_id': mapping.device_id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return create_error_response(str(e)), 500

@user_ns.route('/devices/<string:device_id>')
class UserDevice(Resource):
    @user_ns.doc('remove_user_device')
    @user_ns.marshal_with(user_ns.models['success_response'])
    @user_ns.doc(security='Bearer')
    @jwt_required()
    @user_ns.response(404, 'Device Not Found', user_ns.models['error_response'])
    @user_ns.response(401, 'Authentication Required', user_ns.models['error_response'])
    def delete(self, device_id):
        """Remove device link from current user"""
        try:
            user_id = get_jwt_identity()
            
            mapping = UserDeviceMapping.query.filter_by(
                user_id=user_id,
                device_id=device_id
            ).first()
            
            if not mapping:
                return create_error_response('Device not found for this user'), 404
            
            db.session.delete(mapping)
            db.session.commit()
            
            return {'message': 'Device unlinked successfully'}
            
        except Exception as e:
            db.session.rollback()
            return create_error_response(str(e)), 500