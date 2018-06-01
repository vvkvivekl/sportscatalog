from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Sport, Base, SportItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sports Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///sports.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
    result = json.loads(h.request(url, 'GET')[1])
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
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
    else:
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


# JSON APIs to view Restaurant Information
@app.route('/catalog/<string:sport_name>/items/JSON')
def sportItemsJSON(sport_name):
	temp = session.query(Sport).filter_by(name=sport_name).one()
	sport_id = temp.id
	sport_item = session.query(SportItem).filter_by(
		sport_id=sport_id).all()
	return jsonify(SportItem=[i.serialize for i in sport_item])


@app.route('/catalog/<string:sport_name>/item/<string:sport_item_name>/JSON')
def sportItemJSON(sport_name, sport_item_name):
    Sport_Item = session.query(SportItem).filter_by(name=sport_item_name).one()
    return jsonify(Sport_Item=Sport_Item.serialize)


@app.route('/catalog/JSON')
def sportsJSON():
    sports = session.query(Sport).all()
    return jsonify(sports=[s.serialize for s in sports])


# Show all restaurants
@app.route('/')
@app.route('/catalog/')
def showSport():
	sport = session.query(Sport).order_by(asc(Sport.name))
	sport_item = session.query(SportItem).order_by(SportItem.id.desc()).limit(10)
	list_sport = []
	for sport_item_a in sport_item:
		s_name = session.query(Sport).filter_by(id=sport_item_a.sport_id).one()
		list_sport.append(s_name)
	if 'username' not in login_session:
		#return login_session
		return render_template('publicsports.html', sport=sport, sport_item=sport_item, list_sport=list_sport)
	else:
		#return str(login_session['user_id'])
		return render_template('sports.html', sport=sport, sport_item=sport_item, list_sport=list_sport, login=True)

def getSportById(sport_id):
    sport = session.query(Sport).filter_by(id=sport_id).one()
    return sport

def getSportByName(sport_name):
    sport = session.query(Sport).filter_by(name=sport_name).one()
    return sport

def getAllSports():
	sports = session.query(Sport).order_by(asc(Sport.name))
	return sports

# Show a sport items
@app.route('/catalog/<string:sport_name>/')
@app.route('/catalog/<string:sport_name>/items/')
def showItems(sport_name):
	temp = session.query(Sport).filter_by(name=sport_name).one()
	sport_id = temp.id
	sports = session.query(Sport).order_by(asc(Sport.name))
	sport = session.query(Sport).filter_by(id=sport_id).one()
	sport_item = session.query(SportItem).filter_by(
        sport_id=sport_id).all()
	if 'username' not in login_session:
		return render_template('publicitems.html', sport_item=sport_item, sport=sport, sports=sports)
	else:
		return render_template('items.html', sport_item=sport_item, sport=sport, sports=sports, login=True)

# Show a sport item
@app.route('/catalog/<string:sport_name>/<string:sport_item_name>')
def showItem(sport_name, sport_item_name):
	temp = session.query(Sport).filter_by(name=sport_name).one()
	sport_id = temp.id
	Sport_Item = session.query(SportItem).filter_by(name=sport_item_name, sport_id=sport_id).one()
	sport = session.query(Sport).filter_by(id=sport_id).one()
	if 'username' not in login_session:
		return render_template('publicitem.html', sport_item=Sport_Item, sport=sport)
	else:
		return render_template('publicitem.html', sport_item=Sport_Item, sport=sport, login=True)


# Create a new item
@app.route('/catalog/item/new/', methods=['GET', 'POST'])
def newItem():
	if 'username' not in login_session:
		return redirect('/login')
	sports = session.query(Sport).order_by(asc(Sport.name))
	if login_session['user_id']:
		if request.method == 'POST':
			sport_id = request.form['sport_id']
			sport = session.query(Sport).filter_by(id=sport_id).one()
			newItem = SportItem(name=request.form['name'], description=request.form['description'], sport_id=sport_id, user_id=login_session['user_id'])
			session.add(newItem)
			session.commit()
			flash('New %s Item Successfully Created' % (newItem.name))
			return redirect(url_for('showItems', sport_name=sport.name))
		else:
			return render_template('newsportitem.html', sports=sports, login=True)
"""
# Edit a menu item


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this restaurant. Please create your own restaurant in order to edit items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


# Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete menu items to this restaurant. Please create your own restaurant in order to delete items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)

"""
# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']

        return redirect(url_for('showSport'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showSport'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
