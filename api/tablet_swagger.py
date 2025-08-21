from flask import request
from flask_restx import Namespace, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, EVScanData
from extensions import db, limiter
from utils import create_error_response, create_success_response

# Create namespace
tablet_ns = Namespace('tablet', description='Tablet application operations')

# Request parsers for query parameters
scan_data_parser = reqparse.RequestParser()
scan_data_parser.add_argument('device_id', type=str, help='Filter by specific device ID')
scan_data_parser.add_argument('limit', type=int, default=100, help='Number of records to return (max 1000)')
scan_data_parser.add_argument('offset', type=int, default=0, help='Number of records to skip')
scan_data_parser.add_argument('start_date', type=str, help='Start date filter (ISO format)')
scan_data_parser.add_argument('end_date', type=str, help='End date filter (ISO format)')

@tablet_ns.route('/scan-data')
class TabletScanData(Resource):
    @tablet_ns.doc('get_scan_data_for_tablet')
    @tablet_ns.expect(scan_data_parser)
    @tablet_ns.marshal_with(tablet_ns.models['paginated_scan_response'])
    @tablet_ns.doc(security='Bearer')
    @jwt_required()
    @limiter.limit("200 per minute")  # Note: order matters - jwt_required first
    @tablet_ns.response(401, 'Authentication Required', tablet_ns.models['error_response'])
    @tablet_ns.response(404, 'User Not Found', tablet_ns.models['error_response'])
    def get(self):
        """Get EV scan data for authenticated user's devices
        
        Returns paginated scan data for all devices linked to the authenticated user.
        Supports filtering by device, date range, and pagination.
        """
        try:
            user_id = get_jwt_identity()
            args = scan_data_parser.parse_args()
            
            # Get user's device IDs
            user = User.query.get(user_id)
            if not user:
                return create_error_response('User not found'), 404
            
            device_ids = [mapping.device_id for mapping in user.device_mappings]
            
            if not device_ids:
                return {
                    'scan_data': [],
                    'total_count': 0,
                    'limit': 0,
                    'offset': 0,
                    'has_more': False
                }
            
            # Query parameters
            device_id = args.get('device_id')
            limit = min(args.get('limit', 100), 1000)  # Max 1000 records
            offset = args.get('offset', 0)
            start_date = args.get('start_date')
            end_date = args.get('end_date')
            
            # Build query
            query = EVScanData.query.filter(EVScanData.device_id.in_(device_ids))
            
            # Filter by specific device if requested and user has access
            if device_id and device_id in device_ids:
                query = query.filter(EVScanData.device_id == device_id)
            
            # Date range filtering
            if start_date:
                try:
                    from datetime import datetime
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    query = query.filter(EVScanData.scan_timestamp >= start_dt)
                except ValueError:
                    return create_error_response('Invalid start_date format. Use ISO format.'), 400
            
            if end_date:
                try:
                    from datetime import datetime
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    query = query.filter(EVScanData.scan_timestamp <= end_dt)
                except ValueError:
                    return create_error_response('Invalid end_date format. Use ISO format.'), 400
            
            # Get total count for pagination
            total_count = query.count()
            
            # Execute query with pagination
            scan_data = query.order_by(EVScanData.scan_timestamp.desc()).offset(offset).limit(limit).all()
            
            # Add health status to each record
            scan_data_with_health = []
            for data in scan_data:
                data_dict = data.to_dict()
                data_dict['health_status'] = calculate_device_health(data)
                scan_data_with_health.append(data_dict)
            
            return {
                'scan_data': scan_data_with_health,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }
            
        except Exception as e:
            return create_error_response(str(e)), 500

@tablet_ns.route('/scan-data/<string:scan_id>')
class TabletSingleScanData(Resource):
    @tablet_ns.doc('get_single_scan_data')
    @tablet_ns.marshal_with(tablet_ns.models['scan_data_response'])
    @tablet_ns.doc(security='Bearer')
    @jwt_required()
    @tablet_ns.response(404, 'Scan Data Not Found', tablet_ns.models['error_response'])
    @tablet_ns.response(401, 'Authentication Required', tablet_ns.models['error_response'])
    def get(self, scan_id):
        """Get single scan data record by ID
        
        Returns detailed scan data for a specific scan record.
        User must have access to the device that generated this scan.
        """
        try:
            user_id = get_jwt_identity()
            
            # Get user's device IDs
            user = User.query.get(user_id)
            if not user:
                return create_error_response('User not found'), 404
            
            device_ids = [mapping.device_id for mapping in user.device_mappings]
            
            # Find scan data that belongs to user's devices
            scan_data = EVScanData.query.filter(
                EVScanData.id == scan_id,
                EVScanData.device_id.in_(device_ids)
            ).first()
            
            if not scan_data:
                return create_error_response('Scan data not found'), 404
            
            data_dict = scan_data.to_dict()
            data_dict['health_status'] = calculate_device_health(scan_data)
            
            return data_dict
            
        except Exception as e:
            return create_error_response(str(e)), 500

@tablet_ns.route('/device-status')
class TabletDeviceStatus(Resource):
    @tablet_ns.doc('get_device_status')
    @tablet_ns.marshal_list_with(tablet_ns.models['device_status'])
    @tablet_ns.doc(security='Bearer')
    @jwt_required()
    @tablet_ns.response(401, 'Authentication Required', tablet_ns.models['error_response'])
    def get(self):
        """Get latest status for all user's devices
        
        Returns the most recent scan data and health status for each device
        linked to the authenticated user.
        """
        try:
            user_id = get_jwt_identity()
            
            # Get user's device IDs
            user = User.query.get(user_id)
            if not user:
                return create_error_response('User not found'), 404
            
            device_ids = [mapping.device_id for mapping in user.device_mappings]
            
            if not device_ids:
                return {'devices': []}
            
            # Get latest scan for each device
            device_status = []
            
            for device_mapping in user.device_mappings:
                latest_scan = EVScanData.query.filter_by(
                    device_id=device_mapping.device_id
                ).order_by(EVScanData.scan_timestamp.desc()).first()
                
                device_info = {
                    'device_id': device_mapping.device_id,
                    'device_name': device_mapping.device_name,
                    'latest_scan': latest_scan.to_dict() if latest_scan else None,
                    'last_seen': latest_scan.scan_timestamp.isoformat() if latest_scan else None
                }
                
                # Add health status if scan data exists
                if latest_scan:
                    device_info['health_status'] = calculate_device_health(latest_scan)
                
                device_status.append(device_info)
            
            return {'devices': device_status}
            
        except Exception as e:
            return create_error_response(str(e)), 500

@tablet_ns.route('/device/<string:device_id>/latest')
class TabletLatestDeviceScan(Resource):
    @tablet_ns.doc('get_latest_device_scan')
    @tablet_ns.marshal_with(tablet_ns.models['scan_data_response'])
    @tablet_ns.doc(security='Bearer')
    @jwt_required()
    @tablet_ns.response(403, 'Device Not Accessible', tablet_ns.models['error_response'])
    @tablet_ns.response(404, 'No Scan Data Found', tablet_ns.models['error_response'])
    @tablet_ns.response(401, 'Authentication Required', tablet_ns.models['error_response'])
    def get(self, device_id):
        """Get latest scan data for specific device
        
        Returns the most recent scan data for a specific device.
        User must have access to the specified device.
        """
        try:
            user_id = get_jwt_identity()
            
            # Get user's device IDs
            user = User.query.get(user_id)
            if not user:
                return create_error_response('User not found'), 404
            
            device_ids = [mapping.device_id for mapping in user.device_mappings]
            
            if device_id not in device_ids:
                return create_error_response('Device not accessible by this user'), 403
            
            # Get latest scan for the device
            latest_scan = EVScanData.query.filter_by(
                device_id=device_id
            ).order_by(EVScanData.scan_timestamp.desc()).first()
            
            if not latest_scan:
                return create_error_response('No scan data found for this device'), 404
            
            scan_dict = latest_scan.to_dict()
            scan_dict['health_status'] = calculate_device_health(latest_scan)
            
            return scan_dict
            
        except Exception as e:
            return create_error_response(str(e)), 500

@tablet_ns.route('/analytics/summary')
class TabletAnalyticsSummary(Resource):
    @tablet_ns.doc('get_analytics_summary')
    @tablet_ns.marshal_with(tablet_ns.models['analytics_summary'])
    @tablet_ns.doc(security='Bearer')
    @jwt_required()
    @tablet_ns.response(401, 'Authentication Required', tablet_ns.models['error_response'])
    def get(self):
        """Get analytics summary for user's devices
        
        Returns summary statistics including total devices, scans,
        devices with issues, and last scan timestamp.
        """
        try:
            user_id = get_jwt_identity()
            
            # Get user's device IDs
            user = User.query.get(user_id)
            if not user:
                return create_error_response('User not found'), 404
            
            device_ids = [mapping.device_id for mapping in user.device_mappings]
            
            if not device_ids:
                return {
                    'total_devices': 0,
                    'total_scans': 0,
                    'devices_with_issues': 0,
                    'last_scan_timestamp': None
                }
            
            # Get basic statistics
            total_scans = EVScanData.query.filter(EVScanData.device_id.in_(device_ids)).count()
            
            # Get latest scan timestamp
            latest_scan = EVScanData.query.filter(
                EVScanData.device_id.in_(device_ids)
            ).order_by(EVScanData.scan_timestamp.desc()).first()
            
            # Count devices with recent issues
            devices_with_issues = 0
            for device_id in device_ids:
                latest_device_scan = EVScanData.query.filter_by(
                    device_id=device_id
                ).order_by(EVScanData.scan_timestamp.desc()).first()
                
                if latest_device_scan:
                    health = calculate_device_health(latest_device_scan)
                    if health in ['poor', 'fair']:
                        devices_with_issues += 1
            
            return {
                'total_devices': len(device_ids),
                'total_scans': total_scans,
                'devices_with_issues': devices_with_issues,
                'last_scan_timestamp': latest_scan.scan_timestamp.isoformat() if latest_scan else None
            }
            
        except Exception as e:
            return create_error_response(str(e)), 500

def calculate_device_health(scan_data):
    """Calculate device health based on scan data"""
    if not scan_data:
        return 'unknown'
    
    # Health checks based on acceptable values from Excel file
    checks = []
    
    # Battery checks
    if scan_data.battery_soh is not None:
        checks.append(scan_data.battery_soh >= 70)  # SoH should be >= 70%
    
    if scan_data.battery_temperature is not None:
        checks.append(15.0 <= scan_data.battery_temperature <= 45.0)  # Temperature range
    
    if scan_data.battery_cell_voltage_deviation is not None:
        checks.append(scan_data.battery_cell_voltage_deviation <= 0.04)  # Max 0.04V deviation
    
    if scan_data.battery_temperature_sensor_status:
        checks.append(scan_data.battery_temperature_sensor_status == '정상')
    
    # Motor checks
    if scan_data.motor_torque_value is not None:
        checks.append(950 <= scan_data.motor_torque_value <= 1050)  # Torque range
    
    if scan_data.motor_status:
        checks.append(scan_data.motor_status == '정상')
    
    # Decelerator checks
    if scan_data.decelerator_noise_level is not None:
        checks.append(scan_data.decelerator_noise_level < 100)  # Less than 100dB
    
    if scan_data.decelerator_status:
        checks.append(scan_data.decelerator_status == '정상')
    
    # OBC checks
    if scan_data.obc_status:
        checks.append(scan_data.obc_status == '정상')
    
    if scan_data.bms_status:
        checks.append(scan_data.bms_status == '정상')
    
    # EPCU checks
    if scan_data.epcu_inverter_status:
        checks.append(scan_data.epcu_inverter_status == '정상')
    
    if scan_data.epcu_ldc_status:
        checks.append(scan_data.epcu_ldc_status == '정상')
    
    if scan_data.epcu_vcu_status:
        checks.append(scan_data.epcu_vcu_status == '정상')
    
    # Calculate health percentage
    if not checks:
        return 'unknown'
    
    passed_checks = sum(1 for check in checks if check)
    health_percentage = passed_checks / len(checks)
    
    if health_percentage >= 0.9:
        return 'excellent'
    elif health_percentage >= 0.75:
        return 'good'
    elif health_percentage >= 0.5:
        return 'fair'
    else:
        return 'poor'