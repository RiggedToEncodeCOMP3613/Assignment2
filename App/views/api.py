from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    get_jwt_identity,
    current_user
)
import datetime
import inspect

import App.controllers as controllers

api = Blueprint('api', __name__, url_prefix='/api/v1')


def _get_controller(name):
    return getattr(controllers, name, None)


def _serialize_obj(obj):
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: _serialize_obj(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_serialize_obj(v) for v in obj]
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        return to_dict()
    d = {}
    for k, v in getattr(obj, "__dict__", {}).items():
        if k.startswith("_sa_") or k.startswith("_"):
            continue
        if inspect.isroutine(v):
            continue
        try:
            _ = v.__class__
        except Exception:
            pass
        d[k] = _serialize_obj(v)
    if not d:
        return str(obj)
    return d


def _call_controller(name, *args, **kwargs):
    fn = _get_controller(name)
    if not fn:
        return None, False, f"controller.{name} not implemented"
    result = fn(*args, **kwargs)
    return result, True, None


# Public auth/login - return JWT access token
@api.post('/auth/login')
def login_api():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get('username') or request.form.get('username')
    password = data.get('password') or request.form.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    # Try several common controller function names to find a user and verify password
    finder_names = [
        'get_user_by_username', 'find_user_by_username',
        'get_user', 'get_user_by_name', 'find_user'
    ]
    user = None
    for name in finder_names:
        fn = _get_controller(name)
        if fn:
            try:
                sig = inspect.signature(fn)
                if len(sig.parameters) == 1:
                    user = fn(username)
                else:
                    # fallback: call with username only
                    user = fn(username)
            except Exception:
                try:
                    user = fn(username)
                except Exception:
                    user = None
        if user:
            break

    # If controller has an authenticate function, prefer that
    auth_fn = _get_controller('authenticate') or _get_controller('authenticate_user') or _get_controller('login_user')
    if auth_fn:
        try:
            user = auth_fn(username, password)
            if isinstance(user, str):
                return jsonify({'access_token': user}), 200
        except Exception:
            pass

    if not user:
        return jsonify({'error': 'invalid credentials'}), 401

    # verify password: try controller helper names, or user.check_password method
    verifier = _get_controller('verify_password') or _get_controller('check_password')
    verified = False
    if verifier:
        try:
            verified = verifier(user, password)
        except Exception:
            verified = False
    else:
        check = getattr(user, 'check_password', None) or getattr(user, 'verify_password', None)
        if callable(check):
            try:
                verified = check(password)
            except Exception:
                verified = False
        else:
            if getattr(user, 'password', None) == password:
                verified = True

    if not verified:
        return jsonify({'error': 'invalid credentials'}), 401

    identity = getattr(user, 'id', None) or getattr(user, 'username', username)
    expires = datetime.timedelta(days=7)
    token = create_access_token(identity=identity, expires_delta=expires)
    return jsonify({
        'access_token': token,
        'expires_in': int(expires.total_seconds()),
        'user': _serialize_obj(user)
    }), 200


# User management endpoints
@api.post('/users')
@jwt_required()
def create_user_api():
    fn = _get_controller('create_user') or _get_controller('user_create') or _get_controller('register_user')
    if not fn:
        return jsonify({'error': 'controller.create_user not implemented'}), 501
    data = request.get_json(force=True, silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    user = fn(username, password)
    return jsonify(_serialize_obj(user)), 201


@api.get('/users')
@jwt_required()
def list_users_api():
    fn = _get_controller('list_users') or _get_controller('get_all_users') or _get_controller('users_list')
    if not fn:
        return jsonify({'error': 'controller.list_users not implemented'}), 501
    users = fn()
    return jsonify(_serialize_obj(users)), 200


@api.get('/users/<int:user_id>')
@jwt_required()
def get_user_api(user_id):
    fn = _get_controller('get_user') or _get_controller('find_user')
    if not fn:
        return jsonify({'error': 'controller.get_user not implemented'}), 501
    user = fn(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(_serialize_obj(user)), 200


@api.put('/users/<int:user_id>')
@jwt_required()
def update_user_api(user_id):
    fn = _get_controller('update_user') or _get_controller('edit_user')
    if not fn:
        return jsonify({'error': 'controller.update_user not implemented'}), 501
    data = request.get_json(force=True, silent=True) or {}
    user = fn(user_id, **data)
    return jsonify(_serialize_obj(user)), 200


@api.delete('/users/<int:user_id>')
@jwt_required()
def delete_user_api(user_id):
    fn = _get_controller('delete_user') or _get_controller('remove_user')
    if not fn:
        return jsonify({'error': 'controller.delete_user not implemented'}), 501
    fn(user_id)
    return jsonify({'status': 'deleted'}), 200


# Resident endpoints (list / get / create / inbox)
@api.get('/residents')
@jwt_required()
def list_residents_api():
    fn = _get_controller('list_residents') or _get_controller('get_all_residents') or _get_controller('list_all_residents')
    if not fn:
        lad_fn = _get_controller('list_all_data')
        if lad_fn:
            data = lad_fn()
            return jsonify(_serialize_obj(data.get('residents'))), 200
        return jsonify({'error': 'controller.list_residents not implemented'}), 501
    residents = fn()
    return jsonify(_serialize_obj(residents)), 200


@api.get('/residents/<int:resident_id>')
@jwt_required()
def get_resident_api(resident_id):
    fn = _get_controller('get_resident') or _get_controller('find_resident')
    if not fn:
        return jsonify({'error': 'controller.get_resident not implemented'}), 501
    r = fn(resident_id)
    if not r:
        return jsonify({'error': 'Resident not found'}), 404
    return jsonify(_serialize_obj(r)), 200


@api.post('/residents')
@jwt_required()
def create_resident_api():
    fn = _get_controller('create_resident') or _get_controller('resident_create')
    if not fn:
        return jsonify({'error': 'controller.create_resident not implemented'}), 501
    data = request.get_json(force=True, silent=True) or {}
    r = fn(data.get('name'), data.get('street'))
    return jsonify(_serialize_obj(r)), 201


@api.get('/residents/<int:resident_id>/inbox')
@jwt_required()
def get_resident_inbox_api(resident_id):
    fn = _get_controller('get_resident_inbox') or _get_controller('resident_inbox')
    if not fn:
        return jsonify({'error': 'controller.get_resident_inbox not implemented'}), 501
    street = request.args.get('street')
    inbox = fn(resident_id, street)
    if inbox is None:
        return jsonify({'error': 'Resident not found'}), 404
    return jsonify(_serialize_obj(inbox)), 200


# Driver endpoints (list, get, create, schedule)
@api.get('/drivers')
@jwt_required()
def list_drivers_api():
    fn = _get_controller('list_drivers') or _get_controller('get_all_drivers')
    if not fn:
        lad_fn = _get_controller('list_all_data')
        if lad_fn:
            data = lad_fn()
            return jsonify(_serialize_obj(data.get('drivers'))), 200
        return jsonify({'error': 'controller.list_drivers not implemented'}), 501
    drivers = fn()
    return jsonify(_serialize_obj(drivers)), 200


@api.get('/drivers/<int:driver_id>')
@jwt_required()
def get_driver_api(driver_id):
    fn = _get_controller('get_driver') or _get_controller('find_driver')
    if not fn:
        return jsonify({'error': 'controller.get_driver not implemented'}), 501
    d = fn(driver_id)
    if not d:
        return jsonify({'error': 'Driver not found'}), 404
    return jsonify(_serialize_obj(d)), 200


@api.post('/drivers')
@jwt_required()
def create_driver_api():
    fn = _get_controller('create_driver') or _get_controller('driver_create')
    if not fn:
        return jsonify({'error': 'controller.create_driver not implemented'}), 501
    data = request.get_json(force=True, silent=True) or {}
    d = fn(data.get('status'))
    return jsonify(_serialize_obj(d)), 201


@api.get('/drivers/<int:driver_id>/schedule')
@jwt_required()
def get_driver_schedule_api(driver_id):
    fn = _get_controller('get_driver_schedule') or _get_controller('driver_schedule')
    if not fn:
        return jsonify({'error': 'controller.get_driver_schedule not implemented'}), 501
    schedule = fn(driver_id)
    if schedule is None:
        return jsonify({'error': 'Driver not found'}), 404
    return jsonify(_serialize_obj(schedule)), 200


# Drives endpoints (list / get / create)
@api.get('/drives')
@jwt_required()
def list_drives_api():
    fn = _get_controller('list_drives') or _get_controller('get_all_drives')
    if not fn:
        lad_fn = _get_controller('list_all_data')
        if lad_fn:
            data = lad_fn()
            return jsonify(_serialize_obj(data.get('drives'))), 200
        return jsonify({'error': 'controller.list_drives not implemented'}), 501
    drives = fn()
    return jsonify(_serialize_obj(drives)), 200


@api.get('/drives/<int:drive_id>')
@jwt_required()
def get_drive_api(drive_id):
    fn = _get_controller('get_drive') or _get_controller('find_drive')
    if not fn:
        return jsonify({'error': 'controller.get_drive not implemented'}), 501
    d = fn(drive_id)
    if not d:
        return jsonify({'error': 'Drive not found'}), 404
    return jsonify(_serialize_obj(d)), 200


@api.post('/drives')
@jwt_required()
def create_drive_api():
    fn = _get_controller('create_drive') or _get_controller('drive_create')
    if not fn:
        return jsonify({'error': 'controller.create_drive not implemented'}), 501
    data = request.get_json(force=True, silent=True) or {}
    drive = fn(
        data.get('driver_id'),
        when=data.get('when'),
        current_location=data.get('location')
    )
    if not drive:
        return jsonify({'error': 'Driver not found or create_drive failed'}), 404
    return jsonify(_serialize_obj(drive)), 201


# Stops endpoints (list / get / create)
@api.get('/stops')
@jwt_required()
def list_stops_api():
    fn = _get_controller('list_stops') or _get_controller('get_all_stop_requests') or _get_controller('list_stop_requests')
    if not fn:
        lad_fn = _get_controller('list_all_data')
        if lad_fn:
            data = lad_fn()
            return jsonify(_serialize_obj(data.get('stop_requests')) or _serialize_obj(data.get('stoprequests'))), 200
        return jsonify({'error': 'controller.list_stops not implemented'}), 501
    stops = fn()
    return jsonify(_serialize_obj(stops)), 200


@api.get('/stops/<int:stop_id>')
@jwt_required()
def get_stop_api(stop_id):
    fn = _get_controller('get_stop_request') or _get_controller('get_stop') or _get_controller('find_stop')
    if not fn:
        return jsonify({'error': 'controller.get_stop_request not implemented'}), 501
    s = fn(stop_id)
    if not s:
        return jsonify({'error': 'Stop not found'}), 404
    return jsonify(_serialize_obj(s)), 200


@api.post('/stops')
@jwt_required()
def create_stop_request_api():
    fn = _get_controller('create_stop_request') or _get_controller('stop_request_create')
    if not fn:
        return jsonify({'error': 'controller.create_stop_request not implemented'}), 501
    data = request.get_json(force=True, silent=True) or {}
    stop = fn(
        data.get('resident_id'),
        data.get('drive_id'),
        data.get('street')
    )
    if not stop:
        return jsonify({'error': 'Resident or Drive not found'}), 404
    return jsonify(_serialize_obj(stop)), 201


# Utility: list all data
@api.get('/list-all-data')
@jwt_required()
def api_list_all_data():
    fn = _get_controller('list_all_data')
    if not fn:
        return jsonify({'error': 'controller.list_all_data not implemented'}), 501
    data = fn()
    return jsonify(_serialize_obj(data)), 200