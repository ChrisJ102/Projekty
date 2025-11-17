from flask import abort, jsonify, render_template, flash
from webargs.flaskparser import use_args

from movies_api_app import db, login_manager
from movies_api_app.loans import loans_bp
from movies_api_app.models import Loans, LoansSchema, loans_schema, User, Movie, OrderForm, Shop, MoviesInShop
from movies_api_app.utils import validate_json_content_type, token_required
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from movies_api_app.loans.tasks import askforuser, askforMovie, askformovieinshop, movieinshopupdate, writeLoan

login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@loans_bp.route('/loans/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def create_loan(movie_id):
    form = OrderForm()
    form.shop_id.choices = [(shop.id, shop.city) for shop in Shop.query.all()]
    if form.validate_on_submit():
        load = Loans(movie_id=form.movie_id.data, user_id=form.user_id.data, price=50)
        db.session.add(load)

        db.session.commit()

        form.user_id.data = ''
        form.movie_id.data = ''
        flash("Wypożyczenie zostało złożone pomyślnie")

    return render_template("order.html", form=form, user_id=current_user.id, movie_id=movie_id)


@loans_bp.route('/loans/<int:user1_id>', methods=['GET'])
def get_all_user_loans(user1_id: int):
    User.query.get_or_404(user1_id, description=f'User with id {user1_id} not found')
    loans = Loans.query.filter(Loans.user_id == user1_id).all()

    items = LoansSchema(many=True, exclude=['user']).dump(loans)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })