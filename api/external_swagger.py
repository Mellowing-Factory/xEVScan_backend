from flask import request
from flask_restx import Namespace, Resource
from datetime import datetime
from models import EVScanData
from extensions import db, limiter
from utils import validate_required_fields, create_error_response, create_success_response

# Create namespace
external_ns = Namespace('external', description='External data ingestion operations')

@external_ns.route('/scan-data')
class ExternalScanData(Resource):
    @limiter.limit("100 per minute")  # Higher limit for data ingestion
    @external_ns.doc('receive_scan_data')
    @external_ns.expect(external_ns.models['scan_data_input'])
    @external_ns.marshal_with(external_ns.models['success_response'], code=201)
    @external_ns.response(400, 'Validation Error', external_ns.models['error_response'])
    @external_ns.response(500, 'Internal Server Error', external_ns.models['error_response'])
    def post(self):
        """Receive EV scan data from external server
        
        This endpoint accepts scan data from external EV diagnostic systems.
        All fields except device_id are optional, allowing flexible data ingestion.
        """
        try:
            data = request.get_json()
            
            # Validate required fields
            is_valid, error_message = validate_required_fields(data, ['device_id'])
            if not is_valid:
                return create_error_response(error_message), 400
            
            # Parse scan timestamp or use current time
            scan_timestamp = datetime.utcnow()
            if data.get('scan_timestamp'):
                try:
                    scan_timestamp = datetime.fromisoformat(data['scan_timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    # If parsing fails, use current time
                    pass
            
            # Create new scan data record
            scan_data = EVScanData(
                device_id=data['device_id'],
                scan_timestamp=scan_timestamp,
                
                # Battery data
                battery_total_operation_time=data.get('battery', {}).get('total_operation_time'),
                battery_soh=data.get('battery', {}).get('soh'),
                battery_soc=data.get('battery', {}).get('soc'),
                battery_charge_discharge_cycles=data.get('battery', {}).get('charge_discharge_cycles'),
                battery_estimated_range=data.get('battery', {}).get('estimated_range'),
                battery_cell_voltage_deviation=data.get('battery', {}).get('cell_voltage_deviation'),
                battery_temperature_sensor_status=data.get('battery', {}).get('temperature_sensor_status'),
                battery_temperature=data.get('battery', {}).get('temperature'),
                battery_case_status=data.get('battery', {}).get('case_status'),
                battery_hv_cable_status=data.get('battery', {}).get('hv_cable_status'),
                
                # Motor data
                motor_torque_value=data.get('motor', {}).get('torque_value'),
                motor_status=data.get('motor', {}).get('status'),
                motor_short_open_status=data.get('motor', {}).get('short_open_status'),
                motor_insulation_resistance=data.get('motor', {}).get('insulation_resistance'),
                motor_surge_test=data.get('motor', {}).get('surge_test'),
                
                # Decelerator data
                decelerator_status=data.get('decelerator', {}).get('status'),
                decelerator_torque_rpm=data.get('decelerator', {}).get('torque_rpm'),
                decelerator_noise_level=data.get('decelerator', {}).get('noise_level'),
                decelerator_oil_leak=data.get('decelerator', {}).get('oil_leak'),
                
                # OBC data
                obc_status=data.get('obc', {}).get('status'),
                bms_status=data.get('obc', {}).get('bms_status'),
                
                # EPCU data
                epcu_inverter_status=data.get('epcu', {}).get('inverter_status'),
                epcu_ldc_status=data.get('epcu', {}).get('ldc_status'),
                epcu_vcu_status=data.get('epcu', {}).get('vcu_status'),
                
                # Additional flexible data
                additional_data=data.get('additional_data', {})
            )
            
            db.session.add(scan_data)
            db.session.commit()
            
            return {
                'message': 'Scan data received successfully',
                'scan_id': scan_data.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return create_error_response(str(e)), 500

@external_ns.route('/scan-data/batch')
class ExternalBatchScanData(Resource):
    @limiter.limit("10 per minute")  # Lower limit for batch operations
    @external_ns.doc('receive_batch_scan_data')
    @external_ns.expect(external_ns.models['batch_scan_input'])
    @external_ns.response(201, 'Batch Processing Complete')
    @external_ns.response(400, 'Validation Error', external_ns.models['error_response'])
    @external_ns.response(500, 'Internal Server Error', external_ns.models['error_response'])
    def post(self):
        """Receive multiple EV scan data records in batch
        
        This endpoint allows bulk import of scan data for efficiency.
        Returns summary of successful and failed records.
        """
        try:
            data = request.get_json()
            
            if not data.get('scan_data') or not isinstance(data['scan_data'], list):
                return create_error_response('scan_data array is required'), 400
            
            scan_records = []
            failed_records = []
            
            for i, scan_item in enumerate(data['scan_data']):
                try:
                    # Validate device_id for each record
                    if not scan_item.get('device_id'):
                        failed_records.append({
                            'index': i,
                            'error': 'device_id is required'
                        })
                        continue
                    
                    # Parse scan timestamp
                    scan_timestamp = datetime.utcnow()
                    if scan_item.get('scan_timestamp'):
                        try:
                            scan_timestamp = datetime.fromisoformat(scan_item['scan_timestamp'].replace('Z', '+00:00'))
                        except ValueError:
                            pass
                    
                    # Create scan data record
                    scan_data = EVScanData(
                        device_id=scan_item['device_id'],
                        scan_timestamp=scan_timestamp,
                        
                        # Battery data
                        battery_total_operation_time=scan_item.get('battery', {}).get('total_operation_time'),
                        battery_soh=scan_item.get('battery', {}).get('soh'),
                        battery_soc=scan_item.get('battery', {}).get('soc'),
                        battery_charge_discharge_cycles=scan_item.get('battery', {}).get('charge_discharge_cycles'),
                        battery_estimated_range=scan_item.get('battery', {}).get('estimated_range'),
                        battery_cell_voltage_deviation=scan_item.get('battery', {}).get('cell_voltage_deviation'),
                        battery_temperature_sensor_status=scan_item.get('battery', {}).get('temperature_sensor_status'),
                        battery_temperature=scan_item.get('battery', {}).get('temperature'),
                        battery_case_status=scan_item.get('battery', {}).get('case_status'),
                        battery_hv_cable_status=scan_item.get('battery', {}).get('hv_cable_status'),
                        
                        # Motor data
                        motor_torque_value=scan_item.get('motor', {}).get('torque_value'),
                        motor_status=scan_item.get('motor', {}).get('status'),
                        motor_short_open_status=scan_item.get('motor', {}).get('short_open_status'),
                        motor_insulation_resistance=scan_item.get('motor', {}).get('insulation_resistance'),
                        motor_surge_test=scan_item.get('motor', {}).get('surge_test'),
                        
                        # Decelerator data
                        decelerator_status=scan_item.get('decelerator', {}).get('status'),
                        decelerator_torque_rpm=scan_item.get('decelerator', {}).get('torque_rpm'),
                        decelerator_noise_level=scan_item.get('decelerator', {}).get('noise_level'),
                        decelerator_oil_leak=scan_item.get('decelerator', {}).get('oil_leak'),
                        
                        # OBC data
                        obc_status=scan_item.get('obc', {}).get('status'),
                        bms_status=scan_item.get('obc', {}).get('bms_status'),
                        
                        # EPCU data
                        epcu_inverter_status=scan_item.get('epcu', {}).get('inverter_status'),
                        epcu_ldc_status=scan_item.get('epcu', {}).get('ldc_status'),
                        epcu_vcu_status=scan_item.get('epcu', {}).get('vcu_status'),
                        
                        # Additional flexible data
                        additional_data=scan_item.get('additional_data', {})
                    )
                    
                    scan_records.append(scan_data)
                    
                except Exception as e:
                    failed_records.append({
                        'index': i,
                        'error': str(e)
                    })
            
            # Bulk insert successful records
            if scan_records:
                db.session.bulk_save_objects(scan_records)
                db.session.commit()
            
            return {
                'message': f'Batch processing completed. {len(scan_records)} successful, {len(failed_records)} failed.',
                'successful_records': len(scan_records),
                'failed_records': len(failed_records),
                'failures': failed_records
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return create_error_response(str(e)), 500