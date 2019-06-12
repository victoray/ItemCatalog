import os
import random
import string
import traceback

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, LoginManager, login_required, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from waitress import serve
from db_setup import Base, User, Category, Items

from whitenoise import WhiteNoise


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
login_manager = LoginManager()
login_manager.init_app(app)
flashes = []

users_count = db_session.query(User).count()
categories_count = db_session.query(Category).count()
items_count = db_session.query(Items).count()
counter = list((users_count, categories_count, items_count))


def start():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


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
    items = db_session.query(Items).order_by(Items.id.desc()).limit(5).all()

    db_session.close()
    return render_template('index.html', flashes=reversed(flashes), count=len(flashes),
                           user=current_user, categories=categories, items=items)


@app.route('/register', methods=['POST', 'GET'])
def register():
    db_session = start()

    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            user = User(name=name, email=email, password=password)
            db_session.add(user)
            db_session.commit()
            message = "Registeration Successful"
            flashes.append(message)
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
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = False if request.form.get('remember') is None else True
        print(remember)
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
            flashes.append("Login Successful")
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
        flashes.append("Category Updated")
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
        flashes.append('New Category Added')
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
        flashes.append("{} Deleted".format(category.name))
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
    return render_template('item.html', flashes=reversed(flashes), count=len(flashes), user=current_user, category=category, category_items=category_items)


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

        flashes.append('Item Updated')
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
        item = Items(name=request.form['name'], url=request.form.get('url'), description=request.form.get('description'),
                     user_id=current_user.id, category_id=category_id)
        db_session.add(item)
        db_session.commit()
        db_session.close()
        flashes.append('New Item Added')
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
        flashes.append("{} Deleted".format(item.name))
        flash("{} Deleted".format(item.name))
        return redirect(url_for('item', category_id=category_id))

    db_session.close()
    return render_template('delete-item.html', user=current_user, category=category, item=item)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def page_not_found(e):
    flash('Login Required')
    return render_template('login.html'), 401


if __name__ == "__main__":
    app.secret_key = "".join(random.choice(string.punctuation + string.ascii_letters) for i in range(32))
    app.debug = True
    port = int(os.environ.get('PORT', 8000))
    serve(app, host='0.0.0.0', port=port)
