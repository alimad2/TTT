from flask import Blueprint, request, jsonify, make_response

import service.family_service as service
from rep.mongo import User

family = Blueprint('family', __name__)


@family.route('/family', methods=['POST'])
def create_family():
    """
    @api {post} /family Creates new family
    @apiName NewFamily
    @apiGroup Family

    @apiSuccess (201) {Boolean} result the result of the operation.

    @apiSuccessExample {json} Success-Response:
    {
    "result": true
    }

    @apiError UnauthenticatedError You should login to your account.

    """
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
    this_family = service.create_new_family(username)
    if not this_family:
        return make_response(jsonify({'result': False})), 400
    return make_response(jsonify({'result': True})), 201


@family.route('/family/invited/<string:token>')
def invited(token):
    """
    @api {get} /family:token Accepts the invitation request
    @apiName AcceptInvitation
    @apiGroup Family

    @apiSuccess (200) {Boolean} result The result of the operation.

    @apiSuccessExample {json} Success-Response:
    {
    "result": true
    }

    @apiError UnauthenticatedError You should login to your account.

    """
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
    familyy = service.invited_to_family(username, token)
    if not familyy:
        return make_response(jsonify({'result': False})), 400
    return make_response(jsonify({'result': True})), 200


@family.route('/family/invite')
def invite_member():
    """
    @api {get} /family/invite Invites the user
    @apiName InviteUser
    @apiGroup Family

    @apiSuccess (200) {Boolean} result The result of operation.

    @apiSuccessExample {json} Success-Response:
    {
    "result": true
    }

    @apiParam {String} user Username of user that admin wants to invite to the family.

    @apiError UnauthenticatedError You should login to your account.

    """
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
    """
        @api {get} /family/spends Request All Spends Information for the family.
        @apiName GetAllFamilySpends
        @apiGroup Family

        @apiSuccess {Object[]} spends List of user's spends.
        @apiSuccessExample {json} Success-Response:
        {
        "spends": [
        {
            "category": "car something",
            "date": "25Feb2020",
            "price": 1000,
            "user": "alimad2"
        },
        {
            "category": "car something",
            "date": "23Feb2020",
            "price": 4352,
            "user": "alimad2"
        }
        ]
        }


        @apiError UnauthenticatedError You should login to your account.

        """
    page = request.args.get('page')
    per_page = request.args.get('pp')
    price = request.args.get('price')
    date = request.args.get('date')
    category = request.args.get('category')
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401

    spends = service.family_spends(username, page, per_page, price, date, category)
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
    """
    @api {get} /family/change Owner of family can change members authority.
    @apiName ChangeAuth
    @apiGroup Family

    @apiSuccess (200) {Boolean} result The result of the operation.

    @apiSuccessExample {json} Success-Response:
    {
    "result": true
    }

    @apiParam {String} username Username of the user that owner wants to change his authority.
    @apiParam {Number} to 1=MEMBER, 2=READ, 3=ADMIN



    """
    username = User.decode_token(request.headers.get('Authorization'))
    user_to_be_changed = request.args.get('username')
    to = request.args.get('to')

    result = service.change_user_auth(username, user_to_be_changed, to)

    if result:
        return make_response(jsonify({'result': result})), 400
    else:
        return make_response(jsonify({'result': result})), 200
