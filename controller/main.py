from flask import Blueprint, request, abort, jsonify, url_for, make_response
from jsonschema import validate, ValidationError

import service.service as service
from rep.mongo import User
from service.schema import Spend, Category, CREATE_ROLE, MOCK_ROLE

blue = Blueprint('test', __name__)


@blue.route('/spends', methods=['GET'])
def get_all():
    """
    @api {get} /spends Request All Spends Information
    @apiName GetAllSpends
    @apiGroup Spend

    @apiSuccess {Object[]} spends List of user's spends.
    @apiSuccessExample {json} Success-Response:
    {
    "spends": [
        {
            "category": "smth",
            "date": "10Feb2020",
            "id": 1,
            "price": 500,
            "url": "http://127.0.0.1:5000/spends/1"
        },
        {
            "category": "smth",
            "date": "10Feb2020",
            "id": 2,
            "price": 10,
            "url": "http://127.0.0.1:5000/spends/2"
        }
    ]
    }


    @apiError UnauthenticatedError You should login to your account.
    @apiError NotFoundError Either spend is not available or id is incorrect.

    """

    price = request.args.get('price')
    date = request.args.get('date')
    page = request.args.get('page')
    per_page = request.args.get('pp')
    category = request.args.get('category')
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401

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
    return make_response(jsonify({'spends': spendsJSON})), 200


@blue.route('/spends/<int:spend_id>', methods=['GET'])
def get_spend(spend_id):
    """
    @api {get} /spends:id Request Spend Information
    @apiName GetSpend
    @apiGroup Spend

    @apiSuccess {Number} id The spend id.
    @apiSuccess {date} date Date of spend.
    @apiSuccess {Number} price Price of spend.
    @apiSuccess {Category} category Category of spend.

    @apiParam {Number} id The spend id.

    @apiError UnauthenticatedError You should login to your account.
    @apiError NotFoundError Either spend is not available or id is incorrect.

    """

    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
    spend = service.get_this_spend(username, spend_id)
    if spend == False:
        abort(404)
    spendjson = {
        'id': spend.id,
        'date': spend.date,
        'price': spend.price,
        'category': spend.category.name,
    }
    return make_response(jsonify({'spend': spendjson})), 200


@blue.route('/spends', methods=['POST'])
def new_spend():
    """
    @api {post} /spends Create New Spend
    @apiName NewSpend
    @apiGroup Spend

    @apiSuccess (201) {Number} id The spend id.
    @apiSuccess (201) {date} date Date of spend.
    @apiSuccess (201) {Number} price Price of spend.
    @apiSuccess (201) {Category} category Category of spend.

    @apiSuccessExample {json} Success-Response:
    {
    "spend": {
        "category": "cat",
        "date": "20Feb2020",
        "id": 14,
        "price": 1000
    }
    }

    @apiError BadRequestError Either json request is not available or is not valid.
    @apiError UnauthenticatedError You should login to your account.
    """
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
    print("username is " + str(username))
    if not request.json:
        abort(400)
    try:
        validate(instance=request.json, schema=Spend.get_schema(role=CREATE_ROLE))
    except ValidationError:
        return make_response(jsonify({'result': 'validation error'})), 400

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

    @apiSuccess (200) {Number} id The spend id.
    @apiSuccess (200) {date} date Date of spend.
    @apiSuccess (200) {Number} price Price of spend.
    @apiSuccess (200) {Category} category Category of spend.

    @apiParam {Number} id The spend id.

    @apiError BadRequestError Either json request is not available or is not valid.
    @apiError UnauthenticatedError You should login to your account.


    """
    try:
        validate(instance=request.json, schema=Spend.get_schema(role=MOCK_ROLE))
    except ValidationError:
        return make_response(jsonify({'result': 'validation error'})), 400
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
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

    @apiSuccess (200) {Boolean} result True if spend has been successfully deleted.

    @apiSuccessExample {json} Success-Response:
    {
    "result": true
    }

    @apiParam {Number} id The spend id.

    @apiError BadRequestError Either json request is not available or is not valid.
    @apiError UnauthenticatedError You should login to your account.

    """
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
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

    @apiSuccess {Object[]} categories List of user's categories.

    @apiSuccessExample {json} Success-Response:
    {
    "categories": [
    {
            "description": "this is description of food category",
            "name": "food"
        },
        {
            "description": "this is description of smth category",
            "name": "smth"
        }
    ]
    }


    @apiError BadRequestError Either json request is not available or is not valid.
    @apiError UnauthenticatedError You should login to your account.

    """
    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
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

    @apiSuccess (201) {String} name Category name.
    @apiSuccess (201) {String} description Description of category.
    @apiSuccess (201) {String} message appropriate message.

    @apiSuccessExample {json} Success-Response:
    {
    "category": {
        "description": "this is description of cat category",
        "message": "successfully created",
        "name": "cat"
    }
    }

    @apiError BadRequestError Either json request is not available or is not valid.
    @apiError UnauthenticatedError You should login to your account.

    """
    if not request.json:
        abort(400)
    try:
        validate(instance=request.json, schema=Category.get_schema())
    except ValidationError:
        return make_response(jsonify({'result': 'validation error'})), 400

    username = User.decode_token(request.headers.get('Authorization'))
    if not username:
        return make_response(jsonify({'message': 'please log in again'})), 401
    name = request.json.get('name')
    description = request.json.get('description', 'no description')
    category = {
        'name': name,
        'description': description
    }
    category = service.create_category(username, category)
    categoryJSON = {
        'name': category.name,
        'description': category.description,
        'message': 'successfully created'
    }
    return jsonify({'category': categoryJSON})
