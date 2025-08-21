from flask_restx import Namespace, Resource

# Create namespace
data_spec_ns = Namespace('data-spec', description='Data specification and validation rules')

@data_spec_ns.route('/data-spec')
class DataSpecification(Resource):
    @data_spec_ns.doc('get_data_specification')
    def get(self):
        """Get complete EV scan data specification
        
        Returns the complete data specification based on the Excel file requirements,
        including units, ranges, acceptable values, and descriptions for all EV scan parameters.
        """
        spec = {
            'battery': {
                'total_operation_time': {
                    'unit': '시간',
                    'resolution': 1,
                    'min': 0,
                    'max': '무한',
                    'acceptable': '~',
                    'description': '총 동작시간'
                },
                'soh': {
                    'unit': '%',
                    'resolution': 0.1,
                    'min': 0,
                    'max': 100,
                    'acceptable': 70,
                    'description': 'SoH (State of Health)'
                },
                'soc': {
                    'unit': '%',
                    'resolution': 0.1,
                    'min': 0,
                    'max': 100,
                    'acceptable': '~',
                    'description': 'SoC (State of Charge)'
                },
                'charge_discharge_cycles': {
                    'unit': '회',
                    'resolution': 1,
                    'min': 0,
                    'max': '무한',
                    'acceptable': '~',
                    'description': '충·방전 사이클 수'
                },
                'estimated_range': {
                    'unit': 'km',
                    'resolution': 1,
                    'min': 0,
                    'max': '무한',
                    'acceptable': '~',
                    'description': '예상 주행 가능 거리'
                },
                'cell_voltage_deviation': {
                    'unit': 'V',
                    'resolution': 0.001,
                    'min': 0,
                    'max': 0.04,
                    'acceptable': 0.04,
                    'description': '셀 간 전압 편차',
                    'notes': '단위 : 소수점 3자리'
                },
                'temperature_sensor_status': {
                    'acceptable': '정상',
                    'options': ['정상', '이상'],
                    'description': '온도 센서 이상 유무'
                },
                'temperature': {
                    'unit': '℃',
                    'resolution': 0.1,
                    'min': -127,
                    'max': 127,
                    'acceptable': '15.0~45.0',
                    'description': '배터리 온도'
                },
                'case_status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': '배터리 하부케이스 상태',
                    'notes': 'UI에서 사용자가 직접 입력'
                },
                'hv_cable_status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': '고압케이블 연결상태',
                    'notes': 'UI에서 사용자가 직접 입력'
                }
            },
            'motor': {
                'torque': {
                    'unit': 'Nm',
                    'acceptable': '950~1050',
                    'description': '구동모터',
                    'notes': '표기 방식 2개: Nm 범위 + 정상여부',
                    'notes2': '정상범위 950-1050Nm (비정상 정검요)'
                },
                'status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': '구동모터 상태'
                },
                'short_open_status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': '단락/단선'
                },
                'insulation_resistance': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': '절연저항'
                },
                'surge_test': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': 'surge test'
                }
            },
            'decelerator': {
                'status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': '감속기'
                },
                'torque_rpm': {
                    'unit': 'RPM',
                    'resolution': 1,
                    'acceptable': '950-1050',
                    'description': '토크출력/RPM'
                },
                'noise_level': {
                    'unit': 'dB',
                    'resolution': 1,
                    'acceptable': '<100',
                    'description': '소음 점검'
                },
                'oil_leak': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': '누유',
                    'notes': 'UI에서 사용자가 직접 입력'
                }
            },
            'obc': {
                'status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': 'OBC'
                },
                'bms_status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': 'BMS'
                }
            },
            'epcu': {
                'inverter_status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': '인버터'
                },
                'ldc_status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': 'LDC'
                },
                'vcu_status': {
                    'acceptable': '정상',
                    'options': ['정상', '정검요'],
                    'description': 'VCU'
                }
            }
        }
        
        return {
            'specification': spec,
            'version': '1.0',
            'last_updated': '2025-08-21',
            'categories': ['battery', 'motor', 'decelerator', 'obc', 'epcu'],
            'total_parameters': {
                'battery': 10,
                'motor': 5,
                'decelerator': 4,
                'obc': 2,
                'epcu': 3
            }
        }

@data_spec_ns.route('/data-spec/validation-rules')
class ValidationRules(Resource):
    @data_spec_ns.doc('get_validation_rules')
    def get(self):
        """Get validation rules for EV scan data
        
        Returns comprehensive validation rules for each parameter,
        including data types, ranges, enums, and warning thresholds.
        """
        rules = {
            'battery': {
                'soh': {
                    'type': 'number',
                    'min': 0,
                    'max': 100,
                    'required': False,
                    'warning_threshold': 70
                },
                'soc': {
                    'type': 'number',
                    'min': 0,
                    'max': 100,
                    'required': False
                },
                'temperature': {
                    'type': 'number',
                    'min': -127,
                    'max': 127,
                    'required': False,
                    'acceptable_range': {'min': 15.0, 'max': 45.0}
                },
                'cell_voltage_deviation': {
                    'type': 'number',
                    'min': 0,
                    'max': 0.04,
                    'required': False,
                    'precision': 3
                },
                'temperature_sensor_status': {
                    'type': 'string',
                    'enum': ['정상', '이상'],
                    'required': False
                },
                'case_status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                },
                'hv_cable_status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                }
            },
            'motor': {
                'torque_value': {
                    'type': 'number',
                    'min': 0,
                    'required': False,
                    'acceptable_range': {'min': 950, 'max': 1050}
                },
                'status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                },
                'short_open_status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                },
                'insulation_resistance': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                },
                'surge_test': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                }
            },
            'decelerator': {
                'status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                },
                'torque_rpm': {
                    'type': 'number',
                    'min': 0,
                    'required': False,
                    'acceptable_range': {'min': 950, 'max': 1050}
                },
                'noise_level': {
                    'type': 'number',
                    'min': 0,
                    'required': False,
                    'warning_threshold': 100
                },
                'oil_leak': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                }
            },
            'obc': {
                'status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                },
                'bms_status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                }
            },
            'epcu': {
                'inverter_status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                },
                'ldc_status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                },
                'vcu_status': {
                    'type': 'string',
                    'enum': ['정상', '정검요'],
                    'required': False
                }
            }
        }
        
        return {
            'validation_rules': rules,
            'version': '1.0',
            'description': 'Validation rules for EV scan data based on specifications'
        }