import random
import string

from flask import Flask, render_template, request, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash


from sqlalchemy import create_engine

from db_setup import Base, User, Category, Items

from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(name=name, email=email, password=password)
        db_session.add(user)
        db_session.commit()

        flash("Registeration Successful")
        return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = db_session.query(User).filter(User.email == email).one()
        except:
            return "User Not Found"
        passcheck = check_password_hash(user.password, password)
        flash("Login Successful" if passcheck and user is not None else "Invalid Username/Password")

        return render_template('login.html')

    return render_template('login.html')

@app.route('/resetpassword')
def resetpassword():
    return "reset Password"
@app.route('/category')
def category():
    return render_template('category.html')

@app.route('/category/<int:category_id>/edit')
def edit_category(category_id):
    return "edit category"

@app.route('/category/<int:category_id>/new')
def new_category(category_id):
    return "new category"

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

if __name__ == "__main__":
    app.secret_key = "".join(random.choice(string.punctuation + string.ascii_letters) for i in range(32))
    app.debug = True
    app.run(host="localhost",port=10000)
