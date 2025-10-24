from flask import Blueprint, render_template, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
import json

from App.controllers import (
    create_resident,
    create_driver,
    create_stop_request,
    create_drive,
    get_driver_schedule,
    get_resident_inbox,
    get_resident,
    get_driver
)
from App.controllers.admin import list_all_data
from App.models import Driver, Drive, Resident
from App.database import db

transport_views = Blueprint('transport_views', __name__, template_folder='../templates')

import json
from flask_jwt_extended import get_jwt_identity

def get_identity():
    """Safely get decoded JWT identity (dict instead of string)."""
    identity_raw = get_jwt_identity()
    if isinstance(identity_raw, str):
        try:
            return json.loads(identity_raw)
        except json.JSONDecodeError:
            return {}
    return identity_raw


@transport_views.route('/transport', methods=['GET'])
def transport_page():
    return render_template('transport.html')

@transport_views.route('/api/transport/options', methods=['GET'])
def transport_options():
    data = list_all_data()
    # return drivers, residents and drives to populate dropdowns
    return jsonify({
        'drivers': data.get('drivers', []),
        'residents': data.get('residents', []),
        'drives': data.get('drives', [])
    })

@transport_views.route('/api/transport/create-resident', methods=['POST'])
def api_create_resident():
    payload = request.get_json() or {}

    username = payload.get('username')
    password = payload.get('password')
    name = payload.get('name')
    street = payload.get('street')
    
    r = create_resident(username, password, name=name, street=street)
    return jsonify({
        'message': f"Resident {r.username} created with id {r.id}",
        'id': r.id,
        'name': r.name
    }), 201

    #return jsonify({'id': r.id, 'name': r.name})

@transport_views.route('/api/transport/create-driver', methods=['POST'])
def api_create_driver():
    payload = request.get_json() or {}
    
    username = payload.get('username')
    password = payload.get('password')
    status = payload.get('status')

    d = create_driver(username, password, status=status)
    
    return jsonify({
        'message': f"Driver {d.username} created with id {d.id}",
        'id': d.id,
        'status': d.status
    }), 201
    
    #return jsonify({'id': d.id, 'status': d.status})

@transport_views.route('/api/transport/create-drive', methods=['POST'])
@jwt_required()
def api_create_drive():
    if not isinstance(current_user, Driver):
        return jsonify({"error": "Only drivers can create drives"}), 403
    #if current_user.__class__.__name__.lower() != "driver":
    #    return jsonify({"error": "Only drivers can create drives"}), 403

    payload = request.get_json() or {}
    when = payload.get('when')
    location = payload.get('location')

    drive = create_drive(current_user.id, when=when, current_location=location)
    if not drive:
        return jsonify({'error': 'Drive could not be created'}), 400

    return jsonify({
        'message': f"Drive created for driver {current_user.username}",
        'id': drive.id,
        'driver_id': drive.driver_id,
        'datetime': drive.datetime.strftime("%Y-%m-%d %H:%M"),
        'current_location': drive.current_location
    }), 201

'''@transport_views.route('/api/transport/create-drive', methods=['POST'])
@jwt_required()
def api_create_drive():

    identity = get_identity()
    if identity.get("role") != "driver":
        return jsonify({"error": "Only drivers can create drives"}), 403
    
    payload = request.get_json() or {}

    driver_id = identity.get("id")

    
    driver = get_driver(driver_id)
    #driver = db.session.get(Driver, identity)
    
    
    when = payload.get('when')
    location = payload.get('location')

    drive = create_drive(driver.id, when=when, current_location=location)
    if not drive:
        return jsonify({'error': 'Drive could not be created'}), 400
    
    return jsonify({
        'message': f"Drive created for driver {driver.username}",
        'id': drive.id,
        'driver_id': drive.driver_id,
        'datetime': drive.datetime.strftime("%Y-%m-%d %H:%M"),
        'current_location': drive.current_location
    }), 201'''
    
# return jsonify({'id': drive.id, 'driver_id': drive.driver_id, 'datetime': str(drive.datetime), 'current_location': drive.current_location})
@transport_views.route('/api/transport/create-stop', methods=['POST'])
@jwt_required()
def api_create_stop():
    if current_user.__class__.__name__.lower() != "resident":
        return jsonify({"error": "Only residents can create stop requests"}), 403

    payload = request.get_json() or {}
    drive_id = payload.get('drive_id')
    street = payload.get('street')

    sr = create_stop_request(current_user.id, drive_id, street)
    if not sr:
        return jsonify({'error': 'Stop request could not be created'}), 400

    return jsonify({
        'message': f"Stop request created for resident {current_user.username}",
        'id': sr.id,
        'drive_id': sr.drive_id,
        'requestee_id': sr.requestee_id,
        'street_name': sr.street_name,
        'created_at': sr.created_at.strftime("%Y-%m-%d %H:%M")
    }), 201

'''@transport_views.route('/api/transport/create-stop', methods=['POST'])
@jwt_required()
def api_create_stop():
    #identity = get_jwt_identity()
    identity = get_identity()

    if identity.get("role") != "resident":
        return jsonify({"error": "Only residents can create stop requests"}), 403
    
    payload = request.get_json() or {}

    resident_id = identity.get("id") 
    resident = get_resident(resident_id)

    #resident = db.session.get(Resident, identity)
    drive_id = payload.get('drive_id')
    street = payload.get('street')

    sr = create_stop_request(resident.id, drive_id, street)
    if not sr:
        return jsonify({'error': 'Stop request could not be created'}), 400
    
    return jsonify({
        'message': f"Stop request created for resident {resident.username}",
        'id': sr.id,
        'drive_id': sr.drive_id,
        'requestee_id': sr.requestee_id,
        'street_name': sr.street_name,
        'created_at': sr.created_at.strftime("%Y-%m-%d %H:%M")
    }), 201'''

'''payload = request.get_json() or {}

    resident_id = payload.get('resident_id')
    drive_id = payload.get('drive_id')
    street = payload.get('street')
    sr = create_stop_request(resident_id, drive_id, street)
    if not sr:
        return jsonify({'error': 'Resident or Drive not found'}), 400
    return jsonify({'id': sr.id, 'drive_id': sr.drive_id, 'requestee_id': sr.requestee_id, 'street_name': sr.street_name, 'created_at': str(sr.created_at)})
        '''
    
@transport_views.route('/api/transport/driver-schedule', methods=['GET'])
@jwt_required()
def api_driver_schedule():
    #identity = get_jwt_identity()
    identity = get_identity()

    if identity.get("role") != "driver":
        return jsonify({"error": "Only drivers can view their schedule"}), 403

    driver_id = request.args.get('driver_id', type=int)
    driver = get_driver(driver_id)
    if not driver:
        return jsonify({"error": "Driver not found"}), 404
    
    schedule = get_driver_schedule(driver_id)
    
    result = []
    for d in schedule:
        result.append(
            {
            'id': d.id,
            'datetime': d.datetime.strftime("%Y-%m-%d %H:%M"),
            'driver_id': d.driver_id,
            'stops': [s.id for s in d.stops]
        }
        )
    '''for d in schedule:
        result.append({'id': d.id, 'datetime': str(d.datetime), 'driver_id': d.driver_id, 'stops': [s.id for s in d.stops]})
    '''    
    return jsonify(result), 200

@transport_views.route('/api/transport/resident-inbox', methods=['GET'])
@jwt_required()
def api_resident_inbox():
    #identity = get_jwt_identity()
    identity = get_identity()
    
    if identity.get("role") != "resident":
        return jsonify({"error": "Only residents can view their inbox"}), 403
    
    resident_id = identity.get("id")
    #resident_id = request.args.get('resident_id', type=int)
    
    street = request.args.get('street')
    inbox = get_resident_inbox(resident_id, street)
    
    result = []
    for sr in inbox:
      result.append({
            'id': sr.id,
            'street_name': sr.street_name,
            'requestee_id': sr.requestee_id,
            'drive_id': sr.drive_id,
            'created_at': sr.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(result), 200
    '''for sr in inbox:
        result.append({'id': sr.id, 'street_name': sr.street_name, 'requestee_id': sr.requestee_id, 'drive_id': sr.drive_id, 'created_at': str(sr.created_at)})
    return jsonify(result)'''

@transport_views.route('/api/transport/list-all', methods=['GET'])
def api_list_all():
    data = list_all_data()
    return jsonify(data)

@transport_views.route('/api/transport/update-drive', methods=['POST'])
@jwt_required()
def api_update_drive():
    #identity = get_jwt_identity()
    identity = get_identity()

    if identity.get("role") != "driver":
        return jsonify({"error": "Only drivers can update drives"}), 403
    
    payload = request.get_json() or {}
    drive_id = payload.get('id')
    dt = payload.get('datetime')
    location = payload.get('location')

    driver_id = identity.get("id") 

    drive = db.session.get(Drive, int(drive_id)) if drive_id else None
    if not drive:
        return jsonify({'error': 'Drive not found'}), 404
    
    if drive.driver_id != driver_id:
        return jsonify({'error': 'You can only update your own drives'}), 403

    if dt:
        from datetime import datetime as dtmod
        try:
            drive.datetime = dtmod.fromisoformat(dt)
        except Exception:
            return jsonify({'error': 'Invalid datetime format'}), 400
    
    if location is not None:
        drive.current_location = location
    db.session.commit()

    return jsonify({
        'message': f"Drive updated successfully",
        'id': drive.id,
        'datetime': drive.datetime.strftime("%Y-%m-%d %H:%M"),
        'current_location': drive.current_location
    }), 200

    #return jsonify({'id': drive.id, 'datetime': str(drive.datetime), 'current_location': drive.current_location})
