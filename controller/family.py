from flask import Blueprint, request, jsonify, make_response
from rep.mongo import User
import service.family_service as service

family = Blueprint('family', __name__)


@family.route('/family', methods=['POST'])
def create_family():
    username = User.decode_token(request.headers.get('Authorization'))
    this_family = service.create_new_family(username)
    if not this_family:
        return make_response(jsonify({'result': False})), 400
    return jsonify({'result': True}), 201


@family.route('/family/invited/<string:token>')
def invited(token):
    username = User.decode_token(request.headers.get('Authorization'))
    family = service.invited_to_family(username, token)
    if not family:
        make_response(jsonify({'result': False})), 404
    return make_response(jsonify({'result': True})), 200
