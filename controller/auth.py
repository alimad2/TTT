from flask import Blueprint, request, jsonify, url_for, redirect, make_response
from jsonschema import validate, ValidationError
from werkzeug.security import generate_password_hash

import service.auth_service as service
from service.schema import User, LOGIN_ROLE, REGISTER_ROLE
from rep.mongo import User as us, BlackList
import datetime

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET'])
def register_get():
    return jsonify({'message': 'show registration page'})


@auth.route('/register', methods=['POST'])
def register_post():
    try:
        validate(instance=request.json, schema=User.get_schema(role=REGISTER_ROLE))
    except ValidationError as e:
        print(e)
        return jsonify({'result': 'validation error'})

    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    name = request.json.get('name')

    exist = service.user_already_exists(username=username, email=email)

    if exist:
        return redirect(url_for('auth.register_get'))

    response = service.new_user(username=username, email=email, name=name,
                                password=generate_password_hash(password, method='sha256'))

    return make_response(jsonify(response)), 201


@auth.route('/login', methods=['GET'])
def login_get():
    return jsonify({'login page': 'show login page'})


@auth.route('/login', methods=['POST'])
def login_post():
    try:
        validate(instance=request.json, schema=User.get_schema(role=LOGIN_ROLE))
    except ValidationError as e:
        return jsonify({'result': 'validation error'})

    username = request.json.get('username')
    password = request.json.get('password')

    flag = service.log_user_in(username, password)
    if not flag:
        return redirect(url_for('auth.login_get'))
    else:
        return make_response(jsonify(flag)), 200


@auth.route('/logout')
def logout():
    token = request.headers.get('Authorization')
    BlackList(token=token, blacklisted_on=datetime.datetime.now()).save()
    response_object = {
        'status': 'success',
        'message': 'successfully logged out'
    }
    return make_response(jsonify(response_object)), 200


def get_username(header):
    return us.decode_token(header)
