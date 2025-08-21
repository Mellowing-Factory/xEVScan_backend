from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import JSONB
from extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to device mappings
    device_mappings = db.relationship('UserDeviceMapping', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'device_ids': [mapping.device_id for mapping in self.device_mappings]
        }

class UserDeviceMapping(db.Model):
    __tablename__ = 'user_device_mappings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(db.String(100), nullable=False)
    device_name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'device_id'),)

class EVScanData(db.Model):
    __tablename__ = 'ev_scan_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(100), nullable=False, index=True)
    scan_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Battery data
    battery_total_operation_time = db.Column(db.Float, nullable=True)  # 총 동작시간 (시간)
    battery_soh = db.Column(db.Float, nullable=True)  # SoH (%)
    battery_soc = db.Column(db.Float, nullable=True)  # SoC (%)
    battery_charge_discharge_cycles = db.Column(db.Integer, nullable=True)  # 충·방전 사이클 수
    battery_estimated_range = db.Column(db.Float, nullable=True)  # 예상 주행 가능 거리 (km)
    battery_cell_voltage_deviation = db.Column(db.Float, nullable=True)  # 셀 간 전압 편차 (V)
    battery_temperature_sensor_status = db.Column(db.String(20), nullable=True)  # 온도 센서 이상 유무
    battery_temperature = db.Column(db.Float, nullable=True)  # 배터리 온도 (℃)
    battery_case_status = db.Column(db.String(20), nullable=True)  # 배터리 하부케이스 상태
    battery_hv_cable_status = db.Column(db.String(20), nullable=True)  # 고압케이블 연결상태
    
    # Motor data
    motor_torque_value = db.Column(db.Float, nullable=True)  # 구동모터 토크 (Nm)
    motor_status = db.Column(db.String(20), nullable=True)  # 구동모터 상태
    motor_short_open_status = db.Column(db.String(20), nullable=True)  # 단락/단선
    motor_insulation_resistance = db.Column(db.String(20), nullable=True)  # 절연저항
    motor_surge_test = db.Column(db.String(20), nullable=True)  # surge test
    
    # Decelerator data
    decelerator_status = db.Column(db.String(20), nullable=True)  # 감속기
    decelerator_torque_rpm = db.Column(db.Float, nullable=True)  # 토크출력/RPM
    decelerator_noise_level = db.Column(db.Float, nullable=True)  # 소음 점검 (dB)
    decelerator_oil_leak = db.Column(db.String(20), nullable=True)  # 누유
    
    # OBC data
    obc_status = db.Column(db.String(20), nullable=True)  # OBC
    bms_status = db.Column(db.String(20), nullable=True)  # BMS
    
    # EPCU data
    epcu_inverter_status = db.Column(db.String(20), nullable=True)  # 인버터
    epcu_ldc_status = db.Column(db.String(20), nullable=True)  # LDC
    epcu_vcu_status = db.Column(db.String(20), nullable=True)  # VCU
    
    # JSONB column for additional flexible data
    additional_data = db.Column(JSONB, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'scan_timestamp': self.scan_timestamp.isoformat(),
            'battery': {
                'total_operation_time': self.battery_total_operation_time,
                'soh': self.battery_soh,
                'soc': self.battery_soc,
                'charge_discharge_cycles': self.battery_charge_discharge_cycles,
                'estimated_range': self.battery_estimated_range,
                'cell_voltage_deviation': self.battery_cell_voltage_deviation,
                'temperature_sensor_status': self.battery_temperature_sensor_status,
                'temperature': self.battery_temperature,
                'case_status': self.battery_case_status,
                'hv_cable_status': self.battery_hv_cable_status
            },
            'motor': {
                'torque_value': self.motor_torque_value,
                'status': self.motor_status,
                'short_open_status': self.motor_short_open_status,
                'insulation_resistance': self.motor_insulation_resistance,
                'surge_test': self.motor_surge_test
            },
            'decelerator': {
                'status': self.decelerator_status,
                'torque_rpm': self.decelerator_torque_rpm,
                'noise_level': self.decelerator_noise_level,
                'oil_leak': self.decelerator_oil_leak
            },
            'obc': {
                'status': self.obc_status,
                'bms_status': self.bms_status
            },
            'epcu': {
                'inverter_status': self.epcu_inverter_status,
                'ldc_status': self.epcu_ldc_status,
                'vcu_status': self.epcu_vcu_status
            },
            'additional_data': self.additional_data,
            'created_at': self.created_at.isoformat()
        }