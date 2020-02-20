from flask import Blueprint, request, abort, jsonify, url_for
from jsonschema import validate, ValidationError

import service.service as service
from controller.auth import get_username
from rep.mongo import User
from service.schema import Spend, Category, CREATE_ROLE, MOCK_ROLE

blue = Blueprint('test', __name__)


@blue.route('/spends', methods=['GET'])
def get_all():
    """
    @api {get} /spends Request All Spends Information
    @apiName GetAllSpends
    @apiGroup Spend

    """

    price = request.args.get('price')
    date = request.args.get('date')
    page = request.args.get('page')
    per_page = request.args.get('pp')
    category = request.args.get('category')
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return jsonify({'message': 'please log in again'})

    spends = service.get_all(username, price, date, page, category, per_page)
    spendsJSON = []

    for spend in spends:
        temp = {
            'id': spend.id,
            'date': spend.date,
            'price': spend.price,
            'category': spend.category.name,
            'url': url_for('test.get_spend', spend_id=spend.id, _external=True)
        }
        spendsJSON.append(temp)
    return jsonify({'spends': spendsJSON})


@blue.route('/spends/<int:spend_id>', methods=['GET'])
def get_spend(spend_id):
    """
    @api {get} /spends:id Request Spend Information
    @apiName GetSpend
    @apiGroup Spend

    """

    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return jsonify({'message': 'please log in again'})
    spend = service.get_this_spend(username, spend_id)
    if spend == False:
        abort(404)
    spendjson = {
        'id': spend.id,
        'date': spend.date,
        'price': spend.price,
        'category': spend.category.name,
    }
    return jsonify({'spend': spendjson})


@blue.route('/spends', methods=['POST'])
def new_spend():
    """
    @api {post} /spends Create New Spend
    @apiName NewSpend
    @apiGroup Spend

    """
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return jsonify({'message': 'please log in again'})
    print("username is " + str(username))
    if not request.json:
        abort(400)
    try:
        validate(instance=request.json, schema=Spend.get_schema(role=CREATE_ROLE))
    except ValidationError:
        return jsonify({'result': 'validation error'})

    spend = {
        'date': request.json['date'],
        'price': request.json['price'],
        'category': request.json['category'],
    }
    spend = service.create_spend(username, spend)
    if spend == False:
        abort(400)
    spendjson = {
        'id': spend.id,
        'date': spend.date,
        'price': spend.price,
        'category': spend.category.name,
    }
    return jsonify({'spend': spendjson})


@blue.route('/spends/<int:spend_id>', methods=['PUT'])
def update_spend(spend_id):
    """
    @api {put} /spends:id Update The Spend
    @apiName UpdateSpend
    @apiGroup Spend

    """
    try:
        validate(instance=request.json, schema=Spend.get_schema(role=MOCK_ROLE))
    except ValidationError:
        return jsonify({'result': 'validation error'})
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return jsonify({'message': 'please log in again'})
    price = request.json.get('price', 'nothing')
    date = request.json.get('date', 'nothing')
    category = request.json.get('category', 'nothing')

    ret = service.update_spend(username, spend_id, price, date, category)
    if ret == False:
        abort(404)
    spend = {
        'id': ret.id,
        'date': ret.date,
        'price': ret.price,
        'category': ret.category.name
    }
    return jsonify({'spend': spend})


@blue.route('/spends/<int:spend_id>', methods=['DELETE'])
def delete_spend(spend_id):
    """
    @api {delete} /spends:id Delete The Spend
    @apiName DeleteSpend
    @apiGroup Spend

    """
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return jsonify({'message': 'please log in again'})
    ret = service.delete_spend(username, spend_id)
    if ret == False:
        abort(404)
    return jsonify({'result': True})


@blue.route('/categories', methods=['GET'])
def get_all_categories():
    """
    @api {get} /categories Request All Categories Information
    @apiName GetAllCategories
    @apiGroup Category

    """
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return jsonify({'message': 'please log in again'})
    categories = service.get_all_categories(username)
    categoriesJSON = []
    for category in categories:
        temp = {
            'name': category.name,
            'description': category.description
        }
        categoriesJSON.append(temp)
    return jsonify({'categories': categoriesJSON})


@blue.route('/categories', methods=['POST'])
def create_new_category():
    """
    @api {post} /categories Creates New Category
    @apiName NewCategory
    @apiGroup Category

    """
    if not request.json:
        abort(400)
    try:
        validate(instance=request.json, schema=Category.get_schema())
    except ValidationError:
        return jsonify({'result': 'validation error'})

    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return jsonify({'message': 'please log in again'})
    name = request.json.get('name')
    description = request.json.get('description', 'no description')
    category = {
        'name': name,
        'description': description
    }
    category = service.create_category(username, category)
    categoryJSON = {
        'name': category.name,
        'description': category.description
    }
    return jsonify({'category': categoryJSON})


@blue.route("/testing")
def test():
    auth_header = request.headers.get('Authorization')
    resp = User.decode_token(auth_header)
    user = User.objects(username=resp)
    response_object = {
        'status': 'success',
        'data': {
            'username': get_username(auth_header),
            'email': user[0].email,
        }
    }
    return jsonify(response_object)
