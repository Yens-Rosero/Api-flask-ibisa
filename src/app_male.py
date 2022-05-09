import json
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import pymongo
from bson import json_util

from verify import AuthError

app = Flask(__name__)
URI = "mongodb://localhost:27017/"
app.config["MONGO_URI"] = URI+"IbisaTablas"
mongo = PyMongo(app)

myclient = pymongo.MongoClient(URI)

      
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

# db = mongo.db.users

def _create_database(name):
    mydb = myclient[name]
    return mydb
 
# Crea la base de datos si no existe, la colección si no existe
# e inserta el dato.
@app.route("/api/v1/databases", methods=["POST"])
def create_database():

    mydb = _create_database("devteam")

    mycol = mydb[request.json["name"]]

    #a document
    developer = request.json
    print(developer)

    #insert a document to the collection
    x = mycol.insert_one(developer)
    return jsonify({"data":f"Objeto creado: {x.inserted_id}"}), 201


@app.route("/api/v1/tablas", methods=["GET"])
def lista_tablas():

    mydb = _create_database("devteam")

    collist = mydb.list_collection_names()
    tablas = []
    for db in myclient.list_databases():
        tablas.append({"name": db["name"]})
    return jsonify({"tablas":tablas}), 200


@app.route("/api/v1/tablas/<name>", methods=["GET"])
def lista_datos_tabla(name):
    mydb = _create_database("devteam")
    print("NAME", name)
    mycol = mydb[name]
    resultado = []
    for x in mycol.find():
        if '_id' in x:
            x['_id'] = str(x['_id'])
            resultado.append(x)
    
    print(resultado)
    return jsonify({"data":resultado}), 200

@app.route("/api/v1/tablas/<name>", methods=["DELETE"])
def elimina_tabla(name):
    mydb = _create_database("devteam")
   
    mycol = mydb[name]
    mycol.drop()
    return jsonify({"data":f"Tabla {name} eliminada"}), 204

@app.route("/api/v1/tablas/<name>/<id>", methods=["DELETE"])
def elimina_tabla(name, id):
    mydb = _create_database("devteam")
   
    mycol = mydb[name]
    
    myquery = { "_id": id }

    mycol.delete_one(myquery)
    
    return jsonify({"data":f"Registro {id} de la tabla {name} eliminada"}), 204
    
if __name__ == "__main__":
    app.run(debug=True)
    

