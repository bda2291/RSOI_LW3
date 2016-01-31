import os
from flask import Flask, jsonify, request, url_for
from flask.ext.moment import Moment
from flask.ext.script import Manager, Server
from models import Semantic, db, Function
from sqlalchemy import desc

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

manager = Manager(app)
manager.add_command("runserver", Server(host='127.0.0.1', port=5001))
moment = Moment(app)

@app.route('/semantics/', methods=['POST'])
def new_semantic():
    semantic = request.json.get('semantic')
    function = request.json.get('function')
    if semantic is None or function is None:
        return jsonify({'error': 'function or semantic are lost'}), 400
    try:
        q = Semantic.query.filter_by(semantic=semantic).first()
        a = Function.query.filter_by(name=function).first()
        if q is None:
            q = Semantic.from_json({'semantic': semantic})
            db.session.add(q)
            db.session.commit()
            q.functions.append(a)
            db.session.add(q)
            db.session.commit()
            return jsonify({'semantic_id': q.to_json().get('semantic_id')}), 201
        else:
            return jsonify({'error': 'exists'}), 409
    except:
        return '', 500

@app.route('/semantics/', methods=['GET'])
def get_semantics():
    page = request.args.get('page', 1, type=int)
    try:
        pagination = Semantic.query.order_by(desc(Semantic.time)).paginate(page, per_page=10, error_out=True)
        semantics = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('get_semantics', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('get_semantics', page=page + 1, _external=True)
        return jsonify({
            'total_items': pagination.total,
            'page_number': pagination.page,
            'total_pages': pagination.pages,
            'prev': prev,
            'next': next,
            'semantics': [semantic.to_json() for semantic in semantics]
        }), 200
    except:
        return '', 500

@app.route('/semantics/all', methods=['GET'])
def get_semantics_all():
    try:
        semantics = Semantic.query.all()
        return jsonify({
            'semantics': [semantic.to_json() for semantic in semantics]
        }), 200
    except:
        return '', 500

if __name__ == '__main__':
    manager.run()
