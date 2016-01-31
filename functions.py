import os
from flask import Flask, jsonify, request
from flask.ext.moment import Moment
from flask.ext.script import Manager, Server
from models import Function, db, Semantic

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

manager = Manager(app)
manager.add_command("runserver", Server(host='127.0.0.1', port=5002))
moment = Moment(app)

@app.route('/functions/', methods=['POST'])
def new_function():
    function = request.json.get('function')
    if function is None:
        return jsonify({'error': 'function lost'}), 400
    try:
        a = Function.query.filter_by(name=function).first()
        if a is None:
            a = Function.from_json({'function': function})
            db.session.add(a)
            db.session.commit()
        return jsonify({'function_id': a.to_json().get('function_id')}), 201
    except:
        return '', 500

@app.route('/functions/', methods=['GET'])
def get_functions():
    id_of_semantics = request.json.get('id_of_semantics')
    if id_of_semantics is None:
        return jsonify({'error': 'id of semantics are lost'}), 400
    try:
        dict_of_function = {}
        for id in id_of_semantics:
            a = Semantic.query.filter_by(id=id).first().functions.all()
            if len(a) == 1:
                dict_of_function[id] = str(a[0])
            else:
                dict_of_function[id] = str(a[0]), str(a[1])
        return jsonify({'functions': dict_of_function}), 200
    except:
        return '', 500

@app.route('/functions/one', methods=['GET'])
def get_functions_one():
    id_of_semantics = request.json.get('id_of_semantics')
    if id_of_semantics is None:
        return jsonify({'error': 'id of semantics are lost'}), 400
    try:
        dict_of_function = {}
        a = Semantic.query.filter_by(id=id_of_semantics).first().functions.all()
        if len(a) == 1:
            dict_of_function = str(a[0])
        else:
            dict_of_function = str(a[0]), str(a[1])
        return jsonify({'functions': dict_of_function}), 200
    except:
        return '', 500

if __name__ == '__main__':
    manager.run()