from flask import Blueprint, request, jsonify, make_response

import service.family_service as service
from rep.mongo import User

family = Blueprint('family', __name__)


@family.route('/family', methods=['POST'])
def create_family():
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
    this_family = service.create_new_family(username)
    if not this_family:
        return make_response(jsonify({'result': False})), 400
    return make_response(jsonify({'result': True})), 201


@family.route('/family/invited/<string:token>')
def invited(token):
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
    familyy = service.invited_to_family(username, token)
    if not familyy:
        return make_response(jsonify({'result': False})), 400
    return make_response(jsonify({'result': True})), 200


@family.route('/family/invite')
def invite_member():
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
    invited_user = request.args.get('user')
    flag = service.send_invitation(username, invited_user)
    if flag:
        return make_response(jsonify({'result': True})), 200
    else:
        return make_response(jsonify({'result': False})), 400


@family.route('/family/spends', methods=['GET'])
def get_family_spends():
    page = request.args.get('page')
    per_page = request.args.get('pp')
    price = request.args.get('price')
    date = request.args.get('date')
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401

    spends = service.family_spends(username, page, per_page, price, date)
    if not spends:
        return make_response(jsonify({'message': 'not authorized'})), 401

    spendsJSON = []
    for spend in spends:
        temp = {
            'user': spend.owner.username,
            'date': spend.date,
            'price': spend.price,
            'category': spend.category.name,
        }
        spendsJSON.append(temp)
    return make_response(jsonify({'spends': spendsJSON})), 200


@family.route('/family/change')
def change_user_auth():
    username = User.decode_token(request.headers.get('Authorization'))
    user_to_be_changed = request.args.get('username')
    to = request.args.get('to')

    result = service.change_user_auth(username, user_to_be_changed, to)

    if result:
        return make_response(jsonify({'result': result})), 400
    else:
        return make_response(jsonify({'result': result})), 200
