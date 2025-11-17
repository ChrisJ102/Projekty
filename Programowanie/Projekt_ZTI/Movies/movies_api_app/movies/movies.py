from flask import jsonify, abort, render_template, flash, request
from movies_api_app.movies import movies_bp
from movies_api_app import db, login_manager
from movies_api_app.models import Movie, MovieSchema, Director, Category, PublishingHouse, MovieForm, FindMovieForm, User
from flask_login import login_required


login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@movies_bp.route('/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.order_by(Movie.id)
    return render_template("movies.html", our_movies=movies)


@movies_bp.route('/movies/<int:movie_id>', methods=['GET'])
@login_required
def get_movie(movie_id: int):
    movie = Movie.query.get_or_404(movie_id, description=f'Movie with id {movie_id} not found')
    director = Director.query.get_or_404(movie.director_id)
    ct = Category.query.get_or_404(movie.category_id)
    ph = PublishingHouse.query.get_or_404(movie.publish_house_id)
    return render_template("moviecred.html", our_movie=movie, director=director, ct=ct, ph=ph)


@movies_bp.route('/movies/update/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def update_movie(movie_id: int):
    form = MovieForm()
    movie = Movie.query.get_or_404(movie_id, description=f'Movie with id {movie_id} not found')
    if request.method == "POST":

        movie.title = request.form['title']
        movie.movie_release_year = request.form['movie_release_year']
        movie.movie_rating = request.form['movie_rating']
        description = request.form['description']
        if description is not None:
            movie.description = description
        director_id = request.form['director_id']
        if director_id is not None:
            Director.query.get_or_404(director_id, description=f'Director with id {director_id} not found')
            movie.director_id = director_id
        category_id = request.form['category_id']
        if category_id is not None:
            Category.query.get_or_404(category_id, description=f'Category with id {category_id} not found')
            movie.category_id = category_id
        publish_house_id = request.form['publish_house_id']
        if publish_house_id is not None:
            Director.query.get_or_404(publish_house_id, description=f'Director with id {publish_house_id} not found')
            movie.publish_house_id = publish_house_id
        db.session.commit()
        flash("Movie updated successfully")
        return render_template("modMovie.html", form=form, movie=movie, movie_id=movie_id)
    else:
        return render_template("modMovie.html", form=form, movie=movie, movie_id=movie_id)


@movies_bp.route('/movies/delete/<int:movie_id>')
@login_required
def delete_movie(movie_id: int):
    movie = Movie.query.get_or_404(movie_id, description=f'Movie with id {movie_id} not found')
    try:
        db.session.delete(movie)
        db.session.commit()
        flash("Movie deleted successfully")
        movie = Movie.query.order_by(Movie.id)
        return render_template("movies.html", movie=movie)
    except:
        flash("there was a problem with deleting movie")
        movie = Movie.query.order_by(Movie.id)
        return render_template("movies.html", movie=movie)


@movies_bp.route('/add/movies', methods=['GET', 'POST'])
@login_required
def create_movie():
    form = MovieForm()
    if form.validate_on_submit():

        movie = Movie(
            title=form.title.data,
            movie_release_year=form.movie_release_year.data,
            movie_rating=form.movie_rating.data,
            description=form.description.data,
            cena=form.cena.data,
            director_id=form.director_id.data,
            category_id=form.category_id.data,
            publish_house_id=form.publish_house_id.data
        )

        db.session.add(movie)
        db.session.commit()

        form.title.data = ''
        form.movie_release_year.data = ''
        form.movie_rating.data = ''
        form.description.data = ''
        form.cena.data = ''
        form.director_id.data = ''
        form.category_id.data = ''
        form.publish_house_id.data = ''
        flash("Movie was added successfully")

    return render_template("addMovie.html", form=form)


@movies_bp.route('findmovie', methods=['GET', 'POST'])
def find_movie():
    form = FindMovieForm()
    form.director.choices = [(director.id, director.first_name+director.last_name) for director in Director.query.all()]
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]
    form.publish_house.choices = [(pubhouse.id, pubhouse.name) for pubhouse in PublishingHouse.query.all()]
    if form.validate_on_submit():
        movies = Movie.query.filter(Movie.director_id == form.director.data,
                                  Movie.category_id == form.category.data,
                                  Movie.publish_house_id == form.publish_house.data).all()
        if movies is None:
            flash("No movie was found")
            return render_template("movies.html", our_movies=movies)
        else:
            return render_template("movies.html", our_movies=movies)
    return render_template("findmovie.html", form=form)


@movies_bp.route('/directors/<int:director_id>/movies', methods=['GET'])
def get_all_director_movies(director_id: int):
    Director.query.get_or_404(director_id, description=f'Director with id {director_id} not found')
    movies = Movie.query.filter(Movie.director_id == director_id).all()

    items = MovieSchema(many=True, exclude=['director']).dump(movies)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })


@movies_bp.route('/category/<int:category_id>/movies', methods=['GET'])
def get_all_category_movies(category_id: int):
    Category.query.get_or_404(category_id, description=f'Category with id {category_id} not found')
    movies = Movie.query.filter(Movie.category_id == category_id).all()

    items = MovieSchema(many=True, exclude=['category']).dump(movies)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })


@movies_bp.route('/publishing_house/<int:house_id>/movies', methods=['GET'])
def get_all_house_movies(house_id: int):
    PublishingHouse.query.get_or_404(house_id, description=f'House with id {house_id} not found')
    movies = Movie.query.filter(Movie.publish_house_id == house_id).all()

    items = MovieSchema(many=True, exclude=['publish_house']).dump(movies)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })
