import json, os, requests
from flask import Flask, redirect, url_for, request, make_response, render_template, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.script import Manager
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

URL_FOR_SEMANTICS = 'http://localhost:5001/semantics/'
URL_FOR_FUNCTIONS = 'http://localhost:5002/functions/'
URL_FOR_SESSION = 'http://localhost:5003/session/'

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')

class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

class PostNewSemantic(Form):
    semantic = TextAreaField('Semantic', validators=[Length(5, 1024)])
    function = StringField('Function', validators=[Length(2, 128)])
    submit = SubmitField('Submit')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = {
            'email': form.email.data,
            'password': form.password.data,
            'username': form.username.data,
            'type': 'register'
        }
        response = None
        try:
            response = requests.post(URL_FOR_SESSION, json=new_user)
        except:
            flash('Session is temporarily unavailable')
        if '201' in str(response):
            flash('You can now login.')
            return redirect(url_for('login'))
        else:
            if response is not None:
                error = json.loads(response.text)
                flash(error.get('error'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_information = {
            'email': form.email.data,
            'password': form.password.data,
            'type': 'login'
        }
        response = None
        try:
            response = requests.post(URL_FOR_SESSION, json=login_information)
        except:
            flash('Session is temporarily unavailable')
        if '404' in str(response):
            flash('Invalid email or password.')
        if '200' in str(response):
            token = json.loads(response.text).get('token')
            redirect_to_index = redirect(url_for('index'))
            response = make_response(redirect_to_index)
            response.set_cookie('my_session', value=token)
            return response
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    redirect_to_index = redirect(url_for('index'))
    response = make_response(redirect_to_index)
    response.set_cookie('my_session', value='', expires=0)
    flash('You have been logged out.')
    return response

def check_session():
    token = request.cookies.get('my_session')
    response = requests.post(URL_FOR_SESSION, json={'type': 'token', 'token': token})
    if '200' in str(response):
        return json.loads(response.text).get('username')
    else:
        return 'unregistered'

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PostNewSemantic()
    try:
        user_name = check_session()
    except:
        user_name = 'unregistered'
    login_status = False
    if user_name != 'unregistered':
        login_status = True
        if form.validate_on_submit():
            semantic = form.semantic.data
            function = form.function.data
            try:
                response = requests.post(URL_FOR_FUNCTIONS, json={'function': function})
                function_id = json.loads(response.text).get('function_id')
                response = requests.post(URL_FOR_SEMANTICS, json={'function': function, 'semantic': semantic})
                if json.loads(response.text).get('error') == 'exists':
                    flash('Sorry, same semantic exists')
            except:
                flash('Service is temporarily unavailable')
            return redirect(url_for('index'))
    try:
        page = request.args.get('page', 1, type=int)
        pages = semantics = functions = None
        try:
            response = requests.get(URL_FOR_SEMANTICS + '?page={}'.format(page))
            semantics_in_json = json.loads(response.text)
            id_of_semantics = [x['semantic_id'] for x in semantics_in_json.get('semantics')]
            try:
                response = requests.get(URL_FOR_FUNCTIONS, json={'id_of_semantics': id_of_semantics})
                functions_in_json = json.loads(response.text)
                functions = {}
                for x in functions_in_json.get('functions').items():
                    if len(x) == 2:
                        functions[int(x[0])] = x[1]
                    else:
                        functions[int(x[0])] = x[1], x[2]
            except:
                functions = {x: 'Unknown function' for x in id_of_semantics}
            semantics = semantics_in_json.get('semantics')
            pages = semantics_in_json.get('total_pages')
            semantics.sort(key=lambda x: x['add_time'], reverse=True)
        except:
            pages = 1
            semantics = [{
                'function_id': 101,
                'semantic': 'Unfortunately Dictionary of python are temporarily unavailable',
            }]
            functions = {
                101: 'Technical Team'
            }
        return render_template('index.html', form=form, semantics=semantics, functions=functions, pages=pages, login=login_status,
                               user_name=user_name)
    except:
        return '', 500

@app.route('/list')
def list():
    try:
        pages = semantics = functions = None
        try:
            response = requests.get(URL_FOR_SEMANTICS + 'all')
            semantics_in_json = json.loads(response.text)
            id_of_semantics = [x['semantic_id'] for x in semantics_in_json.get('semantics')]
            try:
                response = requests.get(URL_FOR_FUNCTIONS, json={'id_of_semantics': id_of_semantics})
                functions_in_json = json.loads(response.text)
                functions = {}
                for x in functions_in_json.get('functions').items():
                    if len(x) == 2:
                        functions[int(x[0])] = x[1]
                    else:
                        functions[int(x[0])] = x[1], x[2]
            except:
                functions = {x: 'Unknown function' for x in id_of_semantics}
            semantics = semantics_in_json.get('semantics')
        except:
            semantics = [{
                'function_id': 101,
                'semantic': 'Unfortunately Dictionary of python are temporarily unavailable',
            }]
            functions = {
                101: 'Technical Team'
            }
        return render_template('list.html', semantics=semantics, functions=functions)
    except:
        return '', 500

@app.route('/function/')
def function():
    try:
        id_of_semantics = request.args.get('id', type=int)
        pages = semantics = functions = None
        try:
            response = requests.get(URL_FOR_FUNCTIONS + 'one', json={'id_of_semantics': id_of_semantics})
            functions_in_json = json.loads(response.text)
            functions = {}
            x = functions_in_json.get('functions')
            if type(x) == str:
                functions = x
            else:
                functions = x[0], x[1]
        except:
            functions = {'Unknown function'}
        return render_template('function.html', functions=functions)
    except:
        return '', 500

if __name__ == '__main__':
    manager.run()
