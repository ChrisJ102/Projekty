from flask import jsonify, request, render_template, flash, redirect, url_for
from webargs.flaskparser import use_args

from movies_api_app import db
from movies_api_app.models import MoviesInShop, MoviesInShopSchema, moviesinshops_schema, MovieInShopForm, Shop, Movie
from movies_api_app.utils import validate_json_content_type, get_schema_args, apply_orders, apply_filter, get_pagination, token_required
from movies_api_app.moviesinshop import moviesinship_bp


@moviesinship_bp.route('/addmoviestoshop/<int:shop_id>/<int:movie_id>', methods=['GET', 'POST'])
def add(shop_id, movie_id):
    form = MovieInShopForm()
    if request.method == "POST":
        moviesinshop = MoviesInShop.query.filter(MovieInShopForm.shop_id == form.shop_id.data,
                                              MovieInShopForm.movie_id == form.movie_id.data).first()

        shop = Shop.query.get_or_404(shop_id, description=f'Shop with id {shop_id} not found')
        moviesinshop = MoviesInShop.query.filter(MoviesInShop.shop_id == shop_id).all()
        movies = Movie.query.all()

        moviesinshop.how_many = moviesinshop.how_many + form.how_many.data

        db.session.commit()
        return render_template("shopcred.html", shop=shop, movies=moviesinshop, movie=movies)
    else:
        return render_template("addmoremovies.html", form=form, shop_id=shop_id, movie_id=movie_id)


@moviesinship_bp.route('/addmoviesstoshop/<int:shop_id>', methods=['GET', 'POST'])
def create(shop_id):
    form = MovieInShopForm()
    form.movie.choices = [(movie.id, movie.title) for movie in Movie.query.all()]
    if request.method == "POST":
        movieinshop = MoviesInShop.query.filter(MoviesInShop.shop_id == form.shop.data,
                                              MoviesInShop.movie_id == form.movie.data).first()

        if movieinshop is not None:
            flash("połączenie w bazie już istnieje")
            return redirect(url_for('shops.get_shops'))
        shop = Shop.query.get_or_404(shop_id, description=f'Shop with id {shop_id} not found')
        moviesinshop = MoviesInShop.query.filter(MoviesInShop.shop_id == shop_id).all()
        movies = Movie.query.all()

        if movieinshop is None:
            print(1)
            movieinshop = MoviesInShop(
                shop_id=form.shop.data,
                movie_id=form.movie.data,
                how_many=form.how_many.data
            )

            db.session.add(movieinshop)
            db.session.commit()
            return render_template("shopcred.html", shop=shop, movies=moviesinshop, movie=movies)
        else:
            movieinshop.how_many = movieinshop.how_many + form.how_many.data
        db.session.commit()
        return render_template("shopcred.html", shop=shop, movies=moviesinshop, movie=movies)
    else:
        return render_template("addmoremovies.html", form=form, shop_id=shop_id)


@moviesinship_bp.route('/moviesinshop', methods=['GET'])
def get_bis():
    query = MoviesInShop.query
    schema_args = get_schema_args(MoviesInShop)
    query = apply_orders(MoviesInShop, query)
    query = apply_filter(MoviesInShop, query)
    items, pagination = get_pagination(query, 'moviesinshop.get_bis')

    moviesinshop = MoviesInShopSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': moviesinshop,
        'number_of_records': len(moviesinshop),
        'pagination': pagination
    })


@moviesinship_bp.route('/moviesinshop', methods=['POST'])
@token_required
@validate_json_content_type
@use_args(moviesinshops_schema, error_status_code=400)
def add_director(user_id: int, args: dict):

    bis = MoviesInShop(**args)
    db.session.add(bis)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': moviesinshops_schema.dump(bis)
    }), 201
