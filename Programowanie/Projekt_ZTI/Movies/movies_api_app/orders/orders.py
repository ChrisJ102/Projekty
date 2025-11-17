from flask import jsonify, render_template, flash
from movies_api_app import db, login_manager
from movies_api_app.orders import orders_bp
from movies_api_app.models import Orders, OrdersSchema, User, Movie, OrderForm, Shop
from movies_api_app.tasks import askforuser
from flask_login import login_required, current_user
from movies_api_app.orders.tasks import askforuser, askforMovie, askformovieinshop, movieinshopupdate, writeOrder

login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@orders_bp.route('/orders/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def create_order(movie_id):
    form = OrderForm()
    form.shop_id.choices = [(shop.id, shop.city) for shop in Shop.query.all()]
    if form.validate_on_submit():
        order = Orders(movie_id=form.movie_id.data, user_id=current_user.id)
        db.session.add(order)

        db.session.commit()

        form.user_id.data = ''
        form.movie_id.data = ''
        flash("Zamówienie zostało złożone pomyślnie")

    return render_template("order.html", form=form, user_id=current_user.id, movie_id=movie_id)


@orders_bp.route('/orders/<int:user1_id>', methods=['GET'])
def get_all_user_orders(user1_id: int):
    User.query.get_or_404(user1_id, description=f'User with id {user1_id} not found')
    order = Orders.query.filter(Orders.user_id == user1_id).all()

    items = OrdersSchema(many=True, exclude=['user']).dump(order)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })