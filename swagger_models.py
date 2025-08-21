from flask_restx import fields, Model

def create_swagger_models(api):
    """Create all Swagger models for API documentation"""
    
    # Authentication Models
    auth_register_model = api.model('AuthRegister', {
        'email': fields.String(required=True, description='User email address', example='user@example.com'),
        'password': fields.String(required=True, description='User password (min 8 characters)', example='password123'),
        'name': fields.String(required=True, description='User full name', example='John Doe')
    })
    
    auth_login_model = api.model('AuthLogin', {
        'email': fields.String(required=True, description='User email address', example='user@example.com'),
        'password': fields.String(required=True, description='User password', example='password123')
    })
    
    auth_response_model = api.model('AuthResponse', {
        'access_token': fields.String(description='JWT access token'),
        'user': fields.Nested(api.model('User', {
            'id': fields.String(description='User ID'),
            'email': fields.String(description='User email'),
            'name': fields.String(description='User name'),
            'is_verified': fields.Boolean(description='Email verification status'),
            'created_at': fields.String(description='Account creation timestamp'),
            'device_ids': fields.List(fields.String, description='Linked device IDs')
        }))
    })
    
    # Device Models
    device_add_model = api.model('DeviceAdd', {
        'device_id': fields.String(required=True, description='Unique device identifier', example='EV_DEVICE_001'),
        'device_name': fields.String(description='Human-readable device name', example='Tesla Model S Scanner')
    })
    
    device_response_model = api.model('DeviceResponse', {
        'device_id': fields.String(description='Device ID'),
        'device_name': fields.String(description='Device name'),
        'created_at': fields.String(description='Link creation timestamp')
    })
    
    # EV Scan Data Models
    battery_data_model = api.model('BatteryData', {
        'total_operation_time': fields.Float(description='총 동작시간 (시간)', example=1500.5),
        'soh': fields.Float(description='SoH - State of Health (%)', example=85.2),
        'soc': fields.Float(description='SoC - State of Charge (%)', example=67.8),
        'charge_discharge_cycles': fields.Integer(description='충·방전 사이클 수', example=245),
        'estimated_range': fields.Float(description='예상 주행 가능 거리 (km)', example=420.5),
        'cell_voltage_deviation': fields.Float(description='셀 간 전압 편차 (V)', example=0.025),
        'temperature_sensor_status': fields.String(description='온도 센서 이상 유무', example='정상'),
        'temperature': fields.Float(description='배터리 온도 (℃)', example=28.5),
        'case_status': fields.String(description='배터리 하부케이스 상태', example='정상'),
        'hv_cable_status': fields.String(description='고압케이블 연결상태', example='정상')
    })
    
    motor_data_model = api.model('MotorData', {
        'torque_value': fields.Float(description='구동모터 토크 (Nm)', example=1000.0),
        'status': fields.String(description='구동모터 상태', example='정상'),
        'short_open_status': fields.String(description='단락/단선', example='정상'),
        'insulation_resistance': fields.String(description='절연저항', example='정상'),
        'surge_test': fields.String(description='surge test', example='정상')
    })
    
    decelerator_data_model = api.model('DeceleratorData', {
        'status': fields.String(description='감속기', example='정상'),
        'torque_rpm': fields.Float(description='토크출력/RPM', example=975.0),
        'noise_level': fields.Float(description='소음 점검 (dB)', example=85.5),
        'oil_leak': fields.String(description='누유', example='정상')
    })
    
    obc_data_model = api.model('OBCData', {
        'status': fields.String(description='OBC', example='정상'),
        'bms_status': fields.String(description='BMS', example='정상')
    })
    
    epcu_data_model = api.model('EPCUData', {
        'inverter_status': fields.String(description='인버터', example='정상'),
        'ldc_status': fields.String(description='LDC', example='정상'),
        'vcu_status': fields.String(description='VCU', example='정상')
    })
    
    scan_data_input_model = api.model('ScanDataInput', {
        'device_id': fields.String(required=True, description='Device identifier', example='EV_DEVICE_001'),
        'scan_timestamp': fields.String(description='Scan timestamp (ISO format)', example='2025-08-21T10:30:00'),
        'battery': fields.Nested(battery_data_model, description='Battery scan data'),
        'motor': fields.Nested(motor_data_model, description='Motor scan data'),
        'decelerator': fields.Nested(decelerator_data_model, description='Decelerator scan data'),
        'obc': fields.Nested(obc_data_model, description='OBC scan data'),
        'epcu': fields.Nested(epcu_data_model, description='EPCU scan data'),
        'additional_data': fields.Raw(description='Additional flexible data (JSONB)', example={
            'firmware_version': 'v2.1.5',
            'scan_duration_seconds': 45,
            'operator_id': 'tech_001'
        })
    })
    
    scan_data_response_model = api.model('ScanDataResponse', {
        'id': fields.String(description='Scan record ID'),
        'device_id': fields.String(description='Device ID'),
        'scan_timestamp': fields.String(description='Scan timestamp'),
        'battery': fields.Nested(battery_data_model),
        'motor': fields.Nested(motor_data_model),
        'decelerator': fields.Nested(decelerator_data_model),
        'obc': fields.Nested(obc_data_model),
        'epcu': fields.Nested(epcu_data_model),
        'additional_data': fields.Raw(description='Additional data'),
        'created_at': fields.String(description='Record creation timestamp'),
        'health_status': fields.String(description='Calculated health status', example='excellent')
    })
    
    batch_scan_input_model = api.model('BatchScanInput', {
        'scan_data': fields.List(fields.Nested(scan_data_input_model), required=True, description='Array of scan data records')
    })
    
    # Response Models
    success_response_model = api.model('SuccessResponse', {
        'message': fields.String(description='Success message')
    })
    
    error_response_model = api.model('ErrorResponse', {
        'error': fields.String(description='Error message')
    })
    
    paginated_scan_response_model = api.model('PaginatedScanResponse', {
        'scan_data': fields.List(fields.Nested(scan_data_response_model), description='Array of scan data'),
        'total_count': fields.Integer(description='Total number of records'),
        'limit': fields.Integer(description='Records per page limit'),
        'offset': fields.Integer(description='Current page offset'),
        'has_more': fields.Boolean(description='Whether more records are available')
    })
    
    device_status_model = api.model('DeviceStatus', {
        'device_id': fields.String(description='Device ID'),
        'device_name': fields.String(description='Device name'),
        'latest_scan': fields.Nested(scan_data_response_model, allow_null=True),
        'last_seen': fields.String(description='Last scan timestamp'),
        'health_status': fields.String(description='Current health status')
    })
    
    analytics_summary_model = api.model('AnalyticsSummary', {
        'total_devices': fields.Integer(description='Total number of devices'),
        'total_scans': fields.Integer(description='Total number of scans'),
        'devices_with_issues': fields.Integer(description='Number of devices with issues'),
        'last_scan_timestamp': fields.String(description='Most recent scan timestamp')
    })
    
    return {
        'auth_register': auth_register_model,
        'auth_login': auth_login_model,
        'auth_response': auth_response_model,
        'device_add': device_add_model,
        'device_response': device_response_model,
        'battery_data': battery_data_model,
        'motor_data': motor_data_model,
        'decelerator_data': decelerator_data_model,
        'obc_data': obc_data_model,
        'epcu_data': epcu_data_model,
        'scan_data_input': scan_data_input_model,
        'scan_data_response': scan_data_response_model,
        'batch_scan_input': batch_scan_input_model,
        'success_response': success_response_model,
        'error_response': error_response_model,
        'paginated_scan_response': paginated_scan_response_model,
        'device_status': device_status_model,
        'analytics_summary': analytics_summary_model
    }