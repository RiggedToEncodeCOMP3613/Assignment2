from flask import Blueprint, render_template, jsonify, request

from App.controllers import (
    create_resident,
    create_driver,
    create_stop_request,
    create_drive,
    get_driver_schedule,
    get_resident_inbox
)
from App.controllers.admin import list_all_data
from App.models import Drive
from App.database import db

transport_views = Blueprint('transport_views', __name__, template_folder='../templates')

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
    name = payload.get('name')
    r = create_resident(name)
    return jsonify({'id': r.id, 'name': r.name})

@transport_views.route('/api/transport/create-driver', methods=['POST'])
def api_create_driver():
    payload = request.get_json() or {}
    status = payload.get('status')
    d = create_driver(status)
    return jsonify({'id': d.id, 'status': d.status})

@transport_views.route('/api/transport/create-drive', methods=['POST'])
def api_create_drive():
    payload = request.get_json() or {}
    driver_id = payload.get('driver_id')
    when = payload.get('when')
    location = payload.get('location')
    drive = create_drive(driver_id, when=when, current_location=location)
    if not drive:
        return jsonify({'error': 'Driver not found or error'}), 400
    return jsonify({'id': drive.id, 'driver_id': drive.driver_id, 'datetime': str(drive.datetime), 'current_location': drive.current_location})

@transport_views.route('/api/transport/create-stop', methods=['POST'])
def api_create_stop():
    payload = request.get_json() or {}
    resident_id = payload.get('resident_id')
    drive_id = payload.get('drive_id')
    street = payload.get('street')
    sr = create_stop_request(resident_id, drive_id, street)
    if not sr:
        return jsonify({'error': 'Resident or Drive not found'}), 400
    return jsonify({'id': sr.id, 'drive_id': sr.drive_id, 'requestee_id': sr.requestee_id, 'street_name': sr.street_name, 'created_at': str(sr.created_at)})

@transport_views.route('/api/transport/driver-schedule', methods=['GET'])
def api_driver_schedule():
    driver_id = request.args.get('driver_id', type=int)
    schedule = get_driver_schedule(driver_id)
    result = []
    for d in schedule:
        result.append({'id': d.id, 'datetime': str(d.datetime), 'driver_id': d.driver_id, 'stops': [s.id for s in d.stops]})
    return jsonify(result)

@transport_views.route('/api/transport/resident-inbox', methods=['GET'])
def api_resident_inbox():
    resident_id = request.args.get('resident_id', type=int)
    street = request.args.get('street')
    inbox = get_resident_inbox(resident_id, street)
    result = []
    for sr in inbox:
        result.append({'id': sr.id, 'street_name': sr.street_name, 'requestee_id': sr.requestee_id, 'drive_id': sr.drive_id, 'created_at': str(sr.created_at)})
    return jsonify(result)

@transport_views.route('/api/transport/list-all', methods=['GET'])
def api_list_all():
    data = list_all_data()
    return jsonify(data)

@transport_views.route('/api/transport/update-drive', methods=['POST'])
def api_update_drive():
    payload = request.get_json() or {}
    drive_id = payload.get('id')
    dt = payload.get('datetime')
    location = payload.get('location')
    drive = db.session.get(Drive, int(drive_id)) if drive_id else None
    if not drive:
        return jsonify({'error': 'Drive not found'}), 404
    if dt:
        from datetime import datetime as dtmod
        try:
            drive.datetime = dtmod.fromisoformat(dt)
        except Exception:
            return jsonify({'error': 'Invalid datetime format'}), 400
    if location is not None:
        drive.current_location = location
    db.session.commit()
    return jsonify({'id': drive.id, 'datetime': str(drive.datetime), 'current_location': drive.current_location})
