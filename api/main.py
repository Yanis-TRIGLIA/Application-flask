from flask import Flask, render_template, request, url_for, redirect,jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import ast
import re

app = Flask(__name__)


uri = "mongodb+srv://Admin:admin@cluster0.3xux2wd.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.get_database("flask_db")

figurines = db.figurines


@app.route("/")
def index():
    all_figurines = figurines.find()
    return render_template('index.html', figurines=all_figurines)

@app.route("/create", methods=['POST'])
def create():
    nom = request.form['nom'] 
    prix = request.form['prix']
    serie = request.form['serie']
    personnages = request.form['personnages'].split("/")
    taille = request.form['taille']
    matiere = request.form['matiere']
    editeur = request.form['editeur']
    nbEnStock = request.form['nbEnStock']
    dateDeSortie = request.form['dateDeSortie']
    figurines.insert_one({'nom': nom,
                          'prix': float(prix),
                          'reference':{
                            'serie':serie,
                            'personnages':personnages
                            },
                          'taille':int(taille),
                          'matiere':matiere,
                          'editeur':editeur,
                          'nbEnStock':int(nbEnStock),
                          'dateDeSortie': datetime.strptime(dateDeSortie, "%Y-%m-%d")})
    return redirect(url_for('index'))

@app.route("/<id>/read", methods=['GET'])
def read(id):
    print(id)
    figurine = figurines.find_one({"_id": ObjectId(id)})
    if figurine:
        return render_template('read.html', figurine=figurine)
    else:
        print("Figurine not found")
        return 0

@app.route("/result", methods=['POST'])
def search():
    nom = request.form['nom']
    prix = request.form['prix']
    serie = request.form['serie']
    taille = request.form['taille']
    matiere = request.form['matiere']
    personnage = request.form['personnage']
   
    
    search = {"nom": re.compile(f'.*{nom}.*', re.IGNORECASE)}
    if prix != "":
        search["prix"] = float(prix)
    if serie != "":
        search["reference.serie"] = re.compile(f'.*{serie}.*', re.IGNORECASE)
    if taille != "":
        search["taille"] = int(taille)
    if personnage != "":
        search["reference.personnages"] = re.compile(f'.*{personnage}.*', re.IGNORECASE)
    if matiere != "":
        search["matiere"] = matiere

    figurine = figurines.find(search)

    if figurine:
        return render_template('result.html', figurine=figurine)
    else:
        print("Figurine not exists")
        return 0


@app.route("/<id>/update", methods=['GET'])
def update(id):
    figurine = figurines.find({"_id": ObjectId(id)})
    return render_template('update.html', figurine=figurine)

@app.route("/<id>/commitUpdate", methods=['POST','PUT','PATCH'])
def commitUpdate(id):
    nom = request.form['nom'] 
    prix = request.form['prix']
    serie = request.form['serie']
    personnages = request.form['personnages']
    taille = request.form['taille']
    matiere = request.form['matiere']
    editeur = request.form['editeur']
    nbEnStock = request.form['nbEnStock']
    dateDeSortie = request.form['dateDeSortie']
    filter = { '_id': ObjectId(id) }
    newvalues = { "$set": { 'nom': nom,
                            'prix': float(prix),
                            'reference':{
                                'serie':serie,
                                'personnages':ast.literal_eval(personnages)
                            },
                            'taille':int(taille),
                            'matiere':matiere,
                            'editeur':editeur,
                            'nbEnStock':int(nbEnStock),
                            'dateDeSortie': datetime.strptime(dateDeSortie, "%Y-%m-%d")} }
    figurines.update_one(filter, newvalues)
    return redirect(url_for('index'))

@app.route("/<id>/delete", methods=['POST','DELETE'])
def delete(id):
    figurines.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))


