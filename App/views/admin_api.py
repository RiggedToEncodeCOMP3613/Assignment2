from flask import Blueprint, jsonify, request
from App.controllers import (
    # Data listing functions
    list_all_data, print_users, print_drivers, print_drives,
    print_residents, print_stop_requests, print_all_data,
    # User operations
    create_user, update_user, get_user,
    # Driver operations
    create_driver, get_driver,
    # Drive operations
    create_drive, get_driver_schedule,
    # Resident operations
    create_resident, get_resident,
    # Stop request operations
    create_stop_request, get_resident_inbox
)

admin_api = Blueprint('admin_api', __name__, url_prefix='/api/admin')

# General data endpoints
@admin_api.get('/data')
def get_all_data():
    """Get all database data as JSON."""
    return jsonify(list_all_data())

# User endpoints
@admin_api.get('/users')
def get_users():
    """Get all users."""
    return jsonify(print_users())

@admin_api.post('/users')
def create_new_user():
    """Create a new user."""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'username and password required'}), 400
    
    user = create_user(data['username'], data['password'])
    return jsonify(user.get_json()), 201

@admin_api.put('/users/<int:user_id>')
def update_existing_user(user_id):
    """Update an existing user."""
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'error': 'username required'}), 400
    
    if update_user(user_id, data['username']):
        return jsonify({'message': 'User updated successfully'})
    return jsonify({'error': 'User not found'}), 404

# Driver endpoints
@admin_api.get('/drivers')
def get_drivers_list():
    """Get all drivers."""
    return jsonify(print_drivers())

@admin_api.post('/drivers')
def create_new_driver():
    """Create a new driver."""
    data = request.get_json()
    driver = create_driver(status=data.get('status'))
    return jsonify({'id': driver.id, 'status': driver.status}), 201

@admin_api.get('/drivers/<int:driver_id>/schedule')
def get_schedule(driver_id):
    """Get a driver's schedule."""
    schedule = get_driver_schedule(driver_id)
    if schedule is None:
        return jsonify({'error': 'Driver not found'}), 404
    return jsonify(schedule)

# Drive endpoints
@admin_api.get('/drives')
def get_drives_list():
    """Get all drives."""
    return jsonify(print_drives())

@admin_api.post('/drives')
def create_new_drive():
    """Create a new drive."""
    data = request.get_json()
    if not data or 'driver_id' not in data:
        return jsonify({'error': 'driver_id required'}), 400
    
    drive = create_drive(
        data['driver_id'],
        when=data.get('when'),
        current_location=data.get('current_location')
    )
    if not drive:
        return jsonify({'error': 'Driver not found'}), 404
    return jsonify(drive.get_json() if hasattr(drive, 'get_json') else {'id': drive.id}), 201

# Resident endpoints
@admin_api.get('/residents')
def get_residents_list():
    """Get all residents."""
    return jsonify(print_residents())

@admin_api.post('/residents')
def create_new_resident():
    """Create a new resident."""
    data = request.get_json()
    resident = create_resident(
        name=data.get('name'),
        street=data.get('street')
    )
    return jsonify({'id': resident.id, 'name': resident.name, 'street': resident.street}), 201

@admin_api.get('/residents/<int:resident_id>/inbox')
def get_inbox(resident_id):
    """Get a resident's inbox of stop requests."""
    inbox = get_resident_inbox(resident_id, street=request.args.get('street'))
    if inbox is None:
        return jsonify({'error': 'Resident not found'}), 404
    return jsonify(inbox)

# Stop request endpoints
@admin_api.get('/stop-requests')
def get_stop_requests_list():
    """Get all stop requests."""
    return jsonify(print_stop_requests())

@admin_api.post('/stop-requests')
def create_new_stop_request():
    """Create a new stop request."""
    data = request.get_json()
    if not data or 'resident_id' not in data or 'drive_id' not in data:
        return jsonify({'error': 'resident_id and drive_id required'}), 400
    
    stop_request = create_stop_request(
        data['resident_id'],
        data['drive_id'],
        data.get('street')
    )
    if not stop_request:
        return jsonify({'error': 'Resident or Drive not found'}), 404
    return jsonify({'id': stop_request.id}), 201