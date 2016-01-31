import os
from hashlib import sha256
from uuid import uuid4
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.script import Manager, Server
from models import User, Session, db

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

manager = Manager(app)
manager.add_command("runserver", Server(host='127.0.0.1', port=5003))
moment = Moment(app)

@app.route('/session/', methods=['POST'])
def session():
    type = request.json.get('type')
    if type == 'register':
        try:
            username = request.json.get('username')
            password = request.json.get('password')
            email = request.json.get('email')
            if username is None or username == '' or password is None or password == '' or email is None or email == '':
                return jsonify({'error': 'argumet missing'}), 403
            user = User.query.filter_by(username=username).first()
            if user is not None:
                return jsonify({'error': 'Same user exists'}), 403
            user = User.query.filter_by(email=email).first()
            if user is not None:
                return jsonify({'error': 'Same email exists'}), 403
            user = User(email=email, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return '', 201
        except:
            return '', 500
    if type == 'login':
        try:
            password = request.json.get('password')
            email = request.json.get('email')
            if password is None or password == '' or email is None or email == '':
                return jsonify({'error': 'argumet missing'}), 403
            user = User.query.filter_by(email=email).first()
            if user is not None:
                ses = Session.query.filter_by(user_id=user.to_json().get('user_id')).first()
                if ses is None:
                    token = sha256(str(uuid4()).encode('UTF-8')).hexdigest()
                    expire_time = datetime.now() + timedelta(days=30)
                    ses = Session(user_id=user.to_json().get('user_id'), token=token, expire_time=expire_time)
                    db.session.add(ses)
                    db.session.commit()
                    return jsonify(ses.to_json()), 200
                else:
                    if ses.expire_time > datetime.now():
                        ses.expire_time = (datetime.now() + timedelta(days=30))
                        db.session.add(ses)
                        db.session.commit()
                        return jsonify(ses.to_json()), 200
                    else:
                        db.session.delete(ses)
                        db.session.commit()
                        return '', 404
            return '', 404
        except:
            return '', 500
    if type == 'token':
        try:
            token = request.json.get('token')
            ses = Session.query.filter_by(token=token).first()
            if ses is not None and ses.expire_time > datetime.now():
                user = User.query.filter_by(id=ses.to_json().get('user_id')).first()
                return jsonify(user.to_json()), 200
            return '', 404
        except:
            return '', 500
    return '', 403

if __name__ == '__main__':
    manager.run()




