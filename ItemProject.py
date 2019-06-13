import json
import os
import random
import string
import traceback

import httplib2
from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
from flask_login import login_user, current_user, LoginManager, login_required, logout_user
from oauth2client import client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from validate_email import validate_email
from werkzeug.security import generate_password_hash, check_password_hash
from whitenoise import WhiteNoise

from db_setup import Base, User, Category, Items

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
login_manager = LoginManager()
login_manager.init_app(app)
CLIENT_SECRET_FILE = 'client_secret.json'


def start():
    DBSession = sessionmaker(bind=engine)
    return DBSession()


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    db_session = start()
    # If this request does not have `X-Requested-With` header, this could be a CSRF
    print(request.headers)
    if not request.headers.get('X-Requested-With'):
        abort(403)

    auth_code = request.data

    url = 'https://graph.facebook.com/v3.3/me?access_token={}&fields=name,id,email'.format(str(auth_code).split("'")[1])

    result = httplib2.Http().request(url, 'GET')[1]
    data = json.loads(result)
    name = data['name']
    email = data['email']

    # Get user picture
    url = 'https://graph.facebook.com/v3.3/me/picture?access_token={}&redirect=0&height=200&width=200'.format(
        str(auth_code).split("'")[1])

    result = httplib2.Http().request(url, 'GET')[1]
    data = json.loads(result)
    picture = data['data']['url']

    # Check if user already exists
    old_user = db_session.query(User).filter(User.email == email).first()

    if old_user is None:
        # create new user and login
        user = User(name=name, email=email, picture=picture)
        db_session.add(user)
        db_session.commit()
        login_user(user, remember=True)
    else:
        login_user(old_user, remember=True)

    db_session.close()
    flash("Login Successful, Welcome {}".format(name))
    return redirect(url_for('home'))


@app.route('/gauth', methods=['POST'])
def gauth():
    db_session = start()
    # If this request does not have `X-Requested-With` header, this could be a CSRF
    if not request.headers.get('X-Requested-With'):
        abort(403)

    # Exchange auth code for access token, refresh token, and ID token
    auth_code = request.data
    credentials = client.credentials_from_clientsecrets_and_code(CLIENT_SECRET_FILE, ['profile', 'email'], auth_code)

    # Get profile info from ID token
    userid = credentials.id_token['sub']
    email = credentials.id_token['email']
    name = credentials.id_token['name']
    picture = credentials.id_token['picture']

    # Check if user already exists
    old_user = db_session.query(User).filter(User.email == email).first()

    if old_user is None:
        # create new user and login
        user = User(name=name, email=email, picture=picture)
        db_session.add(user)
        db_session.commit()
        login_user(user)
    else:
        login_user(old_user)

    db_session.close()
    flash("Login Successful, Welcome {}".format(name))
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(user_id):
    db_session = start()
    user = db_session.query(User).filter(User.id == user_id).one()
    db_session.close()
    return user


@app.route('/')
def home():
    db_session = start()
    categories = db_session.query(Category).all()
    items = db_session.query(Items).order_by(Items.id.desc()).limit(8).all()

    db_session.close()
    return render_template('index.html', user=current_user, categories=categories, items=items)


@app.route('/register', methods=['POST', 'GET'])
def register():
    db_session = start()

    if request.method == 'POST':
        try:
            name = "{}".format(request.form['name'])
            if not validate_email(request.form['email'], check_mx=True):
                flash("Invalid Email")
                return render_template('register.html')

            email = request.form['email']
            print(email)
            password = generate_password_hash(request.form['password'])
            user = User(name=name, email=email, password=password)
            db_session.add(user)
            db_session.commit()
            message = "Registration Successful"
            flash(message)
            db_session.close()
            return redirect(url_for('login'))
        except:
            traceback.print_exc()
            flash("User Already Exists. Login Instead")
            db_session.close()
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_session = start()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = False if request.form.get('remember') is None else True
        try:
            user = db_session.query(User).filter(User.email == email).one()
        except:
            traceback.print_exc()
            flash("User Not Found")
            db_session.close()
            return render_template('login.html')

        passcheck = check_password_hash(user.password, password)

        if passcheck:
            login_user(user, remember=remember)
            flash("Login Successful, Welcome {}".format(current_user.name))
            db_session.close()
            return redirect(url_for('home'))
        else:
            flash("Invalid Username/Password")
            db_session.close()
            return render_template('login.html')

    db_session.close()
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Log Out Successful!")
    return redirect(url_for('home'))


@app.route('/resetpassword')
def resetpassword():
    return "reset Password"


@app.route('/category')
def category():
    return render_template('category.html')


@app.route('/<int:category_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_category(category_id):
    db_session = start()

    category = db_session.query(Category).filter(Category.id == category_id).one()

    if request.method == 'POST':
        category.name = request.form['name']
        db_session.commit()
        db_session.close()
        flash("Category Updated")
        return redirect(url_for('home'))

    db_session.close()
    return render_template('edit-category.html', user=current_user, category=category)


@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_category():
    db_session = start()

    if request.method == 'POST':
        category = Category(name=request.form['name'])
        print(category.name)
        db_session.add(category)
        db_session.commit()
        db_session.close()
        flash("New Category Added")
        return redirect(url_for('home'))

    db_session.close()
    return render_template('new-category.html', user=current_user)


@app.route('/<int:category_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    db_session = start()

    category = db_session.query(Category).filter(Category.id == category_id).one()

    if request.method == 'POST':
        db_session.delete(category)
        db_session.commit()
        db_session.close()
        flash("{} Deleted".format(category.name))
        return redirect(url_for('home'))

    db_session.close()
    return render_template('delete-category.html', user=current_user, category=category)


@app.route('/<int:category_id>/')
def item(category_id):
    db_session = start()

    category = db_session.query(Category).filter(Category.id == category_id).one()
    category_items = db_session.query(Items).filter(Items.category_id == category_id).all()

    db_session.close()
    return render_template('item.html', user=current_user,
                           category=category, category_items=category_items)


@app.route('/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(category_id, item_id):
    db_session = start()

    category = db_session.query(Category).filter(Category.id == category_id).one()
    item = db_session.query(Items).filter(Items.id == item_id).one()

    if request.method == 'POST':
        item.name = request.form.get('name')
        item.url = request.form.get('url')
        item.description = request.form.get('description')

        db_session.commit()
        db_session.close()

        flash("Item successfully updated")
        return redirect(url_for('item', category_id=category_id))

    db_session.close()
    return render_template('edit-item.html', user=current_user, category=category, item=item)


@app.route('/<int:category_id>/new', methods=['GET', 'POST'])
@login_required
def new_item(category_id):
    db_session = start()

    category = db_session.query(Category).filter(Category.id == category_id).one()

    if request.method == 'POST':
        item = Items(name=request.form['name'], url=request.form.get('url'),
                     description=request.form.get('description'),
                     user_id=current_user.id, category_id=category_id)
        db_session.add(item)
        db_session.commit()
        db_session.close()
        flash("New Item Added")
        return redirect(url_for('item', category_id=category_id))

    db_session.close()
    return render_template('new-item.html', category=category, user=current_user)


@app.route('/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_item(category_id, item_id):
    db_session = start()

    category = db_session.query(Category).filter(Category.id == category_id).one()
    item = db_session.query(Items).filter(Items.id == item_id).one()

    if request.method == 'POST':
        db_session.delete(item)
        db_session.commit()
        db_session.close()
        flash("{} Deleted".format(item.name))
        return redirect(url_for('item', category_id=category_id))

    db_session.close()
    return render_template('delete-item.html', user=current_user, category=category, item=item)

@app.route('/<int:category_id>/JSON')
def itemJSON(category_id):
    db_session = start()
    items = db_session.query(Items).filter(Items.category_id == category_id).all()

    db_session.close()
    return jsonify(category_items=[i.serialize for i in items])


@app.route('/<int:category_id>/<int:item_id>/JSON')
def categoryJSON(category_id, item_id):
    db_session = start()
    item = db_session.query(Items).filter(Items.id == item_id).one()

    db_session.close()
    return jsonify(Item=item.serialize)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response


@app.errorhandler(401)
def page_not_found(e):
    flash('Login Required')
    return render_template('login.html'), 401


if __name__ == "__main__":
    app.secret_key = "".join(random.choice(string.punctuation + string.ascii_letters) for i in range(32))
    app.debug = True
    port = int(os.environ.get('PORT', 10000))
    # serve(app, host='localhost', port=port)
    app.run(host='localhost', port=port)
