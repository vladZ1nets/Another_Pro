from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import sessionmaker
from database import init_db, db_session
import models

app = Flask(__name__)
app.secret_key = 'hbiuvgtgiujhn'


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        init_db()
        user_data = db_session.execute(select(models.User).filter_by(login=username)).first()
        if user_data:
            session['logged_in'] = user_data.login
            session['user_id'] = user_data.id
            return f'Login successful, welcome {user_data.login}'
        else:
            return 'Wrong username or password', 401


@app.route('/register', methods=['GET', 'POST'])
def register(form_data=None):
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        form_data = dict(request.form)
        init_db()
        user = models.User(**form_data)
        db_session.add(user)
        db_session.commit()
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect('/login')


@app.route('/items', methods=['GET', 'POST'])
@login_required
def items():
    if request.method == 'GET':
        items = db_session.execute(select(models.Item)).scalars().all()
        return render_template('item.html', items=items)
    elif request.method == 'POST':
        if session.get('logged_in') is None:
            return redirect('/login')
        else:
            init_db()
            current_user = db_session.execute(select(models.User).where(models.User.login == session['logged_in'])).scalar()

            new_item = models.Item(**request.form)
            new_item.owner = current_user.id
            db_session.add(new_item)
            db_session.commit()

            return redirect('/items')


@app.route('/items/<int:item_id>', methods=['GET', 'DELETE'])
@login_required
def item_detail(item_id):
    if request.method == 'GET':
        item = db_session.execute(select(models.Item).filter_by(id=item_id)).scalar()
        return render_template('item_detail.html', item=item)
    elif request.method == 'DELETE':
        item = db_session.execute(select(models.Item).filter_by(id=item_id)).scalar()
        if item:
            db_session.delete(item)
            db_session.commit()
            return redirect('/items')
        return 'Item not found', 404


@app.route('/profile', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@app.route('/me', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@login_required
def profile():
    if request.method == 'GET':
        user = db_session.execute(select(models.User).filter_by(id=session['user_id'])).scalar()
        return render_template('user.html', fullname=user.full_name)
    elif request.method == 'PUT':
        user = db_session.execute(select(models.User).filter_by(id=session['user_id'])).scalar()
        user.full_name = request.form.get('full_name')
        db_session.commit()
        return redirect('/profile')
    elif request.method == 'DELETE':
        user = db_session.execute(select(models.User).filter_by(id=session['user_id'])).scalar()
        db_session.delete(user)
        db_session.commit()
        session.pop('user_id', None)
        session.pop('logged_in', None)
        return redirect('/login')


@app.route('/profile/favorites', methods=['GET', 'POST', 'DELETE', 'PATCH'])
@login_required
def favorites():
    user_id = session['user_id']
    if request.method == 'GET':
        favorites = db_session.execute(select(models.Favorite).filter_by(user_id=user_id)).scalars().all()
        return render_template('favorites.html', favorites=favorites)
    elif request.method == 'POST':
        new_favorite = models.Favorite(user_id=user_id, item_id=request.form['item_id'])
        db_session.add(new_favorite)
        db_session.commit()
        return redirect('/profile/favorites')
    elif request.method == 'DELETE':
        favorite = db_session.execute(select(models.Favorite).filter_by(user_id=user_id, item_id=request.form['item_id'])).scalar()
        if favorite:
            db_session.delete(favorite)
            db_session.commit()
        return redirect('/profile/favorites')


@app.route('/profile/favorites/<int:favourite_id>', methods=['DELETE'])
def favorite_detail(favourite_id):
    favorite = db_session.execute(select(models.Favorite).filter_by(id=favourite_id)).scalar()
    if favorite:
        db_session.delete(favorite)
        db_session.commit()
        return redirect('/profile/favorites')
    return 'Favorite not found', 404


@app.route('/profile/search_history', methods=['GET', 'DELETE'])
@login_required
def search_history():
    user_id = session['user_id']
    if request.method == 'GET':
        history = db_session.execute(select(models.SearchHistory).filter_by(user_id=user_id)).scalars().all()
        return render_template('search_history.html', history=history)
    elif request.method == 'DELETE':
        db_session.execute(delete(models.SearchHistory).filter_by(user_id=user_id))
        db_session.commit()
        return redirect('/profile/search_history')


@app.route('/leasers', methods=['GET'])
@login_required
def leasers():
    leasers = db_session.execute(select(models.User).filter(models.User.role == 'leaser')).scalars().all()
    return render_template('leasers.html', leasers=leasers)


@app.route('/leasers/<int:leaser_id>', methods=['GET'])
@login_required
def leaser_detail(leaser_id):
    leaser = db_session.execute(select(models.User).filter_by(id=leaser_id)).scalar()
    return render_template('leaser_detail.html', leaser=leaser)


@app.route('/contracts', methods=['GET', 'POST'])
@login_required
def contracts():
    if request.method == 'GET':
        contracts = db_session.execute(select(models.Contract)).scalars().all()
        return render_template('contracts.html', contracts=contracts)
    elif request.method == 'POST':
        contract_data = request.form.to_dict()
        new_contract = models.Contract(**contract_data)
        db_session.add(new_contract)
        db_session.commit()
        return redirect('/contracts')


@app.route('/contracts/<int:contract_id>', methods=['GET', 'PATCH', 'PUT'])
@login_required
def contract_detail(contract_id):
    if request.method == 'GET':
        contract = db_session.execute(select(models.Contract).filter_by(id=contract_id)).scalar()
        return render_template('contract_detail.html', contract=contract)
    elif request.method == 'PATCH':
        contract = db_session.execute(select(models.Contract).filter_by(id=contract_id)).scalar()
        contract.status = 'updated'
        db_session.commit()
        return redirect(f'/contracts/{contract_id}')
    elif request.method == 'PUT':
        pass


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        search_query = request.form['query']
        results = db_session.execute(select(models.Item).filter(models.Item.name.ilike(f'%{search_query}%'))).scalars().all()
        return render_template('search_results.html', results=results)


@app.route('/complain', methods=['POST'])
def complain():
    pass


@app.route('/compare', methods=['GET', 'PUT', 'PATCH'])
@login_required
def compare():
    if request.method == 'GET':
        return render_template('compare.html')
    elif request.method in ['PUT', 'PATCH']:
        pass


if __name__ == '__main__':
    app.run(debug=True)
