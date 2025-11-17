from flask import jsonify
from celery import shared_task
from movies_api_app.models import User, Movie, MoviesInShop, Orders
from movies_api_app import db


@shared_task
def divide(x, y):
    import time
    time.sleep(5)
    return x/y


@shared_task
def askforuser(user_id: int):
    user = User.query.get_or_404(user_id)
    return user.id


@shared_task
def askforMovie(movie_id):
    movie = Movie.query.get_or_404(movie_id, description=f'Movie with id {movie_id} not found')
    return movie.id


@shared_task
def askformovieinshop(movie_id, shop_id):
    moviewhere = MoviesInShop.query.filter(MoviesInShop.movie_id == movie_id,
                                         MoviesInShop.shop_id == shop_id).first()
    if moviewhere is None:
        return -1
    else:
        return moviewhere.how_many


@shared_task
def movieinshopupdate(movie_id, shop_id):
    moviewhere = MoviesInShop.query.filter(MoviesInShop.movie_id == movie_id,
                                         MoviesInShop.shop_id == shop_id).first()
    moviewhere.how_many = moviewhere.how_many - 1
    db.session.commit()
    return moviewhere.how_many


@shared_task
def writeOrder(user_id, movie_id):
    order = Orders(user_id=user_id, movie_id=movie_id)
    print(order.id)
    db.session.add(order)
    db.session.commit()
    return 'zamowienie zapisane do bazy'


@shared_task
def MovieList():
    movies = Movie.query.order_by(Movie.id)
    return jsonify({
        'data': movies
    })
