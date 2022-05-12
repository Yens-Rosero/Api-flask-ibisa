import json
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import pymongo
from bson import json_util
from verify import AuthError, requires_auth, get_tenant
from bson.objectid import ObjectId

app = Flask(__name__)
URI = "mongodb+srv://yens:123@cluster.ijc7x.mongodb.net/"
app.config["MONGO_URI"] = URI+"IbisaTablas"
mongo = PyMongo(app)

myclient = pymongo.MongoClient(URI)


def _create_database(name):
    mydb = myclient[name[0]]
    return mydb
 
# Crea la base de datos si no existe, la colección si no existe
# e inserta el dato.
@app.route("/api/v1/databases", methods=["POST"])
@requires_auth
def create_database():
    tenant = get_tenant()
    mydb = _create_database(tenant)

    mycol = mydb[request.json["name"]]

    #a document
    developer = request.json
    print(developer)

    #insert a document to the collection
    x = mycol.insert_one(developer)
    return jsonify({"data":f"Objeto creado: {x.inserted_id}"}), 201


@app.route("/api/v1/tablas", methods=["GET"])
@requires_auth
def lista_tablas():
    tenant = get_tenant()

    mydb = _create_database(tenant)

    collist = mydb.list_collection_names()
    tablas = []
    for db in myclient.list_databases():
        tablas.append({"name": db["name"]})
    return jsonify({"tablas":tablas}), 200


@app.route("/api/v1/tablas/<name>", methods=["GET"])
@requires_auth
def lista_datos_tabla(name):
    tenant = get_tenant()
    mydb = _create_database(tenant)
    mycol = mydb[name]
    resultado = []
    for x in mycol.find():
        if '_id' in x:
            x['_id'] = str(x['_id'])
            resultado.append(x)
    
    print(resultado)
    return jsonify({"data":resultado}), 200

@app.route("/api/v1/tablas/<name>", methods=["DELETE"])
@requires_auth
def elimina_tabla(name):
    tenant = get_tenant()
    mydb = _create_database(tenant)
   
    mycol = mydb[name]
    mycol.drop()
    return jsonify({"data":f"Tabla {name} eliminada"}), 204

@app.route("/api/v1/tablas/<name>/<id>", methods=["DELETE"])
@requires_auth
def elimina_campo(name, id):
    tenant = get_tenant()
    mydb = _create_database(tenant)
    
    mycol = mydb[name]
    
    myquery = { "_id": id }

    mycol.delete_one(myquery)
    
    return jsonify({"data":f"Registro {id} de la tabla {name} eliminada"}), 204

@app.route('/api/v1/tablas/<name>/<id>', methods=["PUT"])
@requires_auth
def update_user(name, id):
    tenant = get_tenant()
    
    mydb = _create_database(tenant)
    
    mycol = mydb[name]
    
    print(mycol , "ESTO ES MY COL")
    
    mycol.update_one(
        {'_id': ObjectId(id)}, {'$set': request.json})
    
    response = jsonify({'message': 'User ' + id + ' Updated Successfuly'}) , 200

    return response

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
    
if __name__ == "__main__":
    app.run(debug=True)
    

