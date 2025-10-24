from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user, unset_jwt_cookies, create_access_token, set_access_cookies
from App.models import User, Driver, Resident
from App.database import db

import json

from.index import index_views

from App.controllers import (
    login,

)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(request.referrer)
    if not token:
        flash('Bad username or password given'), 401
    else:
        flash('Login Successful')
        set_access_cookies(response, token) 
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''
@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(message='Username and password required'), 400

    user = Resident.query.filter_by(username=username).first()
    if not user:
        user = Driver.query.filter_by(username=username).first()
    if not user:
        user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify(message='Bad username or password given'), 401

    access_token = create_access_token(identity=user)

    response = jsonify({
        "message": f"Logged in as {user.username}",
        "access_token": access_token,
        "role": user.__class__.__name__.lower()
    })
    set_access_cookies(response, access_token)
    return response, 200

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    identity = get_jwt_identity() or {}

    username = getattr(current_user, 'username', 'unknown')
    user_id = identity.get('id', 'unknown')
    role = identity.get('role', current_user.__class__.__name__.lower() if current_user else 'unknown')

    return jsonify({
        'message': f"User identified: username={username}, id={user_id}, role={role}"
    }), 200


@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response, 200