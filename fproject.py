from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


app = Flask(__name__)


def connectdb():
    """Connect to the db and return a session"""
    engine = create_engine('sqlite:///restaurantMenu.db')
    Base.metadata.bind=engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    return session


@app.route('/restaurants/JSON/')
def restaurantsJSON():
    session = connectdb()
    items = session.query(Restaurant).all()
    return jsonify(Restaurants=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
    session = connectdb()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    session = connectdb()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant.id, id=menu_id).one()
    return jsonify(MenuItem=[item.serialize])


@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    """show all restaurants"""
    session = connectdb()
    items = session.query(Restaurant).all()
    return render_template('restaurants.html', items=items)


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    """show the menu for a restaurant"""
    session = connectdb()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)

 
@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
    """add a new restaurant"""
    if request.method == 'POST':
        session = connectdb()
        newRestaurant = Restaurant(name = request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash("new restaurant created")
        return redirect(url_for('showRestaurants'))
    return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    """edit restaurant"""
    session = connectdb()
    item = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if len(request.form['name']) > 0:
            item.name = request.form['name']
        session.add(item)
        session.commit()
        flash("restaurant edited")
        return redirect(url_for('showRestaurants'))
    return render_template('editRestaurant.html', item=item)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    "delete restaurant"
    session = connectdb()
    item = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("restaurant deleted")
        return redirect(url_for('showRestaurants'))
    return render_template('deleteRestaurant.html', item=item)


@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    """new menu item"""
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], 
            description=request.form['description'],
            price=request.form['price'],
            course=request.form['course'],
            restaurant_id=restaurant_id)
        session = connectdb()
        session.add(newItem)
        session.commit()
        flash("new menu item created")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    """edit menu item"""
    session = connectdb()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if len(request.form['name']) > 0:
            item.name = request.form['name']
        if len(request.form['description']) > 0:
            item.description = request.form['description']
        if len(request.form['price']) > 0:
            item.price = request.form['price']
        if len(request.form['course']) > 0:
            item.course = request.form['course']
        session.add(item)
        session.commit()
        flash("menu item edited")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=item)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    """delete menu item"""
    session = connectdb()
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(menuItem)
        session.commit()
        flash("menu item deleted")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', item=menuItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
