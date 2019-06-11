import random
import string
import traceback

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, LoginManager, login_required, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

from db_setup import Base, User, Category, Items

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

app = Flask(__name__)
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
    db_session.close()
    return render_template('index.html', flashes=flashes, count=len(flashes),
                           user=current_user, counter=counter, categories=categories)


@app.route('/register', methods=['POST', 'GET'])
def register():
    print(flashes)

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
            return redirect(url_for('login'))
        except:
            flash("User Already Exists. Login Instead")
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


@app.route('/category/<int:category_id>/edit')
def edit_category(category_id):
    return "edit category"


@app.route('/new')
def new_category():
    return render_template('new-category.html', user=current_user)


@app.route('/category/<int:category_id>/delete')
def delete_category(category_id):
    return "delete category"


@app.route('/category/<int:category_id>/')
def item(category_id):
    return "item"


@app.route('/category/<int:category_id>/<int:item_id>/edit')
def edit_item(category_id, item_id):
    return "edit category"


@app.route('/category/<int:category_id>/<int:item_id>/new')
def new_item(category_id, item_id):
    return "new category"


@app.route('/category/<int:category_id>/<int:item_id>/delete')
def delete_item(category_id, item_id):
    return "delete category"


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
    app.run(host="localhost", port=10000)
