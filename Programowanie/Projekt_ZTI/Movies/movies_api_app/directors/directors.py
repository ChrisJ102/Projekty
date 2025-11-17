from flask import render_template, flash, request

from movies_api_app import db, login_manager
from movies_api_app.models import Director, DirectorForm, User
from movies_api_app.directors import directors_bp
from flask_login import login_required

login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@directors_bp.route('/directors', methods=['GET'])
def get_directors():
    directors = Director.query.order_by(Director.id)
    return render_template("directors.html", our_directors=directors)


@directors_bp.route('/directors/<int:director_id>', methods=['GET'])
@login_required
def get_director(director_id: int):
    director = Director.query.get_or_404(director_id, description=f'Director with id {director_id} not found')
    return render_template("directorcreds.html", our_director=director)


@directors_bp.route('/add/director', methods=['GET', 'POST'])
@login_required
def add_director():
    form = DirectorForm()
    if form.validate_on_submit():
        director = Director(first_name=form.first_name.data, last_name=form.last_name.data, birth_date=form.birth_date.data)
        db.session.add(director)
        db.session.commit()

        form.first_name.data = ''
        form.last_name.data = ''
        form.birth_date.data = ''
        flash("Director was added successfully")

    return render_template("addDirector.html", form=form)


@directors_bp.route('/mod/directors/<int:director_id>', methods=['GET', 'POST'])
@login_required
def update_director(director_id: int):
    form = DirectorForm()
    director = Director.query.get_or_404(director_id, description=f'Director with id {director_id} not found')
    if request.method == "POST":

        director.first_name = request.form['first_name']
        director.last_name = request.form['last_name']
        director.birth_date = request.form['birth_date']
        db.session.commit()
        flash("Director updated successfully")
        return render_template("modAut.html", form=form, director=director, director_id=director_id)
    else:
        return render_template("modAut.html", form=form, director=director, director_id=director_id)


@directors_bp.route('/directors/delete/<int:director_id>')
@login_required
def delete_director(director_id: int):
    director = Director.query.get_or_404(director_id, description=f'Director with id {director_id} not found')
    try:
        db.session.delete(director)
        db.session.commit()
        flash("Director deleted successfully")
        our_directors = Director.query.order_by(Director.id)
        return render_template("directors.html", our_directors=our_directors)
    except:
        flash("there was a problem with deleting director")
        our_directors = Director.query.order_by(Director.id)
        return render_template("directors.html", our_directors=our_directors)
