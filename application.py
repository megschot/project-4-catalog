from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

import random
import string
import json
import httplib2
import requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from database_setup import Base, User, Category, CatalogItem

app = Flask(__name__)

# Create client ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Get user ID
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Create user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Create anti-forgery state token
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Create '/gconnect'
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is'
                                            'already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Check if user exists, make new user if it doesn't.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token'
                                            ' for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Making API Endpoint for '/categories/JSON'
@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


# Making API Endpoint for '/category/<int:category_id>/JSON'
@app.route('/category/<int:category_id>/JSON')
def categoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return jsonify(category=category.serialize)


# Making API Endpoint for '/items/JSON'
@app.route('/items/JSON')
def itemsJSON():
    items = session.query(CatalogItem).all()
    return jsonify(items=[i.serialize for i in items])


# Making API Endpoint for '/item/<int:item_id>/JSON'
@app.route('/item/<int:item_id>/JSON')
def itemJSON(item_id):
    item = session.query(CatalogItem).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


# Routing for main page
@app.route('/')
@app.route('/category')
def main_page():
    categories = session.query(Category).order_by(asc(Category.name))
    # Show 10 most recent items
    items = session.query(CatalogItem).order_by(desc(CatalogItem.id)).limit(10)
    return render_template('main.html', categories=categories, items=items)


# Routing for item page
@app.route('/catalog/<string:category_name>/<string:item_name>')
def view_items(category_name, item_name):
    selected_item = session.query(CatalogItem).join(Category).filter(
        CatalogItem.name == item_name).filter(
        Category.name == category_name).one()
    return render_template('item.html', item=selected_item)


# Routing for main page to display items for cateogory
@app.route('/catalog/<string:category_name>/items')
def show_items(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    selected_category = session.query(Category).filter_by(
        name=category_name).one()
    return render_template('main.html', categories=categories,
                           category=selected_category)


# Routing for new items
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def new_item():
    categories = session.query(Category).all()
    # Confirm user is logged in - if not redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = CatalogItem(name=request.form['name'],
                              description=request.form['description'],
                              category_id=request.form['category'],
                              user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New item has been created!')
        return redirect(url_for('view_items',
                                category_name=newItem.category.name,
                                item_name=newItem.name))
    return render_template('new_item.html', categories=categories)


# Routing for edit item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    # Confirm user is logged in - if not redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    edited_item = session.query(CatalogItem).filter_by(name=item_name).one()
    categories = session.query(Category).all()
    if edited_item.user_id != login_session['user_id']:
        flash('You are not authorized to edit this item.')
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        edited_item.name = request.form['name']
        edited_item.description = request.form['description']
        edited_item.category_id = request.form['category']
        session.merge(edited_item)
        session.commit()
        flash('Item has been edited!')
        return redirect(url_for('view_items',
                                category_name=edited_item.category.name,
                                item_name=edited_item.name))
    else:
        return render_template('edit_item.html',
                               categories=categories,
                               item=edited_item)


# Routing for delete item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    #  Confirm user is logged in - if not redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    deleted_item = session.query(CatalogItem).filter_by(name=item_name).one()
    if deleted_item.user_id != login_session['user_id']:
        flash('You are not authorized to delete this item.')
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        session.delete(deleted_item)
        session.commit()
        # Send message to user in main.html
        flash('Your item has been deleted')
        return redirect(url_for('main_page'))
    else:
        return render_template('delete_item.html',
                               item=deleted_item)


# Logout based on provider
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('main_page'))
    else:
        flash("You were not logged in")
        return redirect(url_for('main_page'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0')
