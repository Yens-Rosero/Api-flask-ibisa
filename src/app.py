import re
from flask import Flask, jsonify, request, Response, _request_ctx_stack
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from regex import R
from werkzeug.security import generate_password_hash, check_password_hash
import json
from six.moves.urllib.request import urlopen
from functools import wraps
from cryptography.hazmat.primitives import serialization
from flask_cors import cross_origin
from jose import jwt
import http.client
from verify import AuthError, requires_auth, get_tenant


AUTH0_DOMAIN = 'ibisa.auth0.com'
API_AUDIENCE = 'https://ibisa.co/api'
ALGORITHMS = ["RS256"]


app = Flask(__name__)


@app.route('/boards/api/v1', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_users():
    tenant = get_tenant()
    app.config['MONGO_URI'] = 'mongodb+srv://yens:123@cluster.ijc7x.mongodb.net/' + \
        tenant[0]+'?retryWrites=true&w=majority'
    mongo = PyMongo(app)
    collection = mongo.db.list_collection_names()
    collection = json.dumps(collection)

    print("collections:", collection, "\n")
    # content = mongo.db[collection].find()
    # content = json_util.dumps(content)
    # print("content:", content, "\n")
    # all = [content, collection]
    return Response(collection, mimetype="application/json")


@app.route('/boards/api/v1', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_user():
    # Receiving Data
    tenant = get_tenant()
    app.config['MONGO_URI'] = 'mongodb+srv://yens:123@cluster.ijc7x.mongodb.net/' + \
        tenant[0]+'?retryWrites=true&w=majority'

    mongo = PyMongo(app)
    content = request.json['content']
    # username = request.json['username']
    # email = request.json['email']
    # password = request.json['password']
    id = mongo.db[content].insert(request.json)
    response = jsonify({
        '_id': str(id),
    })
    response.status_code = 201
    return response


@app.route('/boards/api/v1/<content>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_user(content):
    print(content)
    tenant = get_tenant()
    app.config['MONGO_URI'] = 'mongodb+srv://yens:123@cluster.ijc7x.mongodb.net/' + \
        tenant[0]+'?retryWrites=true&w=majority'

    mongo = PyMongo(app)
    board = mongo.db[content].find()
    response = json_util.dumps(board)
    return Response(response, mimetype="application/json")


@app.route('/boards/api/v1/<content>', methods=['DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def delete_user(content):
    tenant = get_tenant()
    app.config['MONGO_URI'] = 'mongodb+srv://yens:123@cluster.ijc7x.mongodb.net/' + \
        tenant[0]+'?retryWrites=true&w=majority'
    content = request.json['content']
    mongo = PyMongo(app)
    print(content, " CONTENT")
    mongo.db[content].drop({})
    response = jsonify(
        {'message': 'content' + content + ' Deleted Successfully'})
    response.status_code = 200
    return response


@app.route('/boards/api/v1/<content>/<id>', methods=['PUT'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def update_user(content, id):
    tenant = get_tenant()
    app.config['MONGO_URI'] = 'mongodb+srv://yens:123@cluster.ijc7x.mongodb.net/' + \
        tenant[0]+'?retryWrites=true&w=majority'
    mongo = PyMongo(app)
    content = request.json['content']
    data = json_util.dumps(request.json)
    print(data, " CONTENT")
    mongo.db[content].update_one(
        {'_id': ObjectId(id)}, {'$set': request.json})
    response = jsonify({'message': 'User ' + id + 'Updated Successfuly'})
    response.status_code = 200
    return response


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'message': 'Resource Not Found ' + request.url,
        'status': 404
    }
    response = jsonify(message)
    response.status_code = 404
    return response


if __name__ == "__main__":
    app.run(debug=True, port=8080)
