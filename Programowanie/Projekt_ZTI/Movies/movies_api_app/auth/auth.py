from flask import abort, jsonify, render_template, flash, request, redirect, url_for
from webargs.flaskparser import use_args

from movies_api_app import db, login_manager
from movies_api_app.auth import auth_bp
from movies_api_app.models import User, user_schema, user_password_update_schema, UserForm, LoginForm, Orders, Loans, Movie
from flask_login import login_user, login_required, logout_user, current_user


login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/xd', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("base.html")


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    username = None
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            password = User.generate_hashed_password(form.password1.data)
            user = User(username=form.username.data, email=form.email.data, password=password)
            db.session.add(user)
            db.session.commit()
        username = form.username.data
        form.username.data = ''
        form.email.data = ''
        form.password1.data = ''
        flash("User was added successfully")

    our_users = User.query.order_by(User.creation_date)
    return render_template("users.html", form=form, username=username, our_users=our_users)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.is_password_valid(request.form['password']):
                login_user(user)
                flash("Login succeeded")
                return redirect(url_for('auth.get_current_user'))
            else:
                flash("Wrong password, try again!")
        else:
            flash("That user doesn't exist")
    return render_template('login.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been log out!")
    return redirect(url_for('auth.login'))


@auth_bp.route('/user', methods=['GET', 'POST'])
@login_required
def get_current_user():
    orders = Orders.query.filter(Orders.user_id == current_user.id).order_by(Orders.buy_date)
    loans = Loans.query.filter(Loans.user_id == current_user.id).order_by(Loans.start_date)
    movies = Movie.query.all()
    return render_template("usercred.html", orders=orders, loans=loans, movies=movies)


@auth_bp.route('/modifypassword/<int:user_id>', methods=['GET', 'POST'])
def change_password(user_id: int):
    form = UserForm()
    user_to_update = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")
    if request.method == "POST":

        user = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")

        if user.is_password_valid(request.form['password1']):
            user.password = user.generate_hashed_password(request.form['password2'])
            flash("User updated successfully")
        else:
            flash("Wrong password")

        db.session.commit()
        return render_template("updtpwd.html", form=form, user_to_update=user_to_update)
    else:
        return render_template("updtpwd.html", form=form, user_to_update=user_to_update, user_id=user_id)


@auth_bp.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update_user_data(user_id: int):
    form = UserForm()
    user_to_update = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")
    if request.method == "POST":
        if User.query.filter(User.username == request.form['username']).first():
            abort(409, description=f'User with username {request.form["username"]} already exists')
        if User.query.filter(User.email == request.form['email']).first():
            abort(409, description=f'User with email {request.form["email"]} already exists')

        user = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")

        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash("User updated successfully")
        return render_template("updateuser.html", form=form, user_to_update=user_to_update, user_id=user_id)

    else:
        return render_template("updateuser.html", form=form, user_to_update=user_to_update, user_id=user_id)


@auth_bp.route('/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")
    username = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully")
        our_users = User.query.order_by(User.creation_date)
        return render_template("users.html", form=form, username=username, our_users=our_users)

    except:
        flash("there was a problem with deleting user")
        our_users = User.query.order_by(User.creation_date)
        return render_template("users.html", form=form, username=username, our_users=our_users)


@auth_bp.route('/update/password', methods=['PUT'])
@use_args(user_password_update_schema, error_status_code=400)
def update_user_password(user_id: int, args: dict):
    user = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")

    if not user.is_password_valid(args['current_password']):
        abort(401, description="Invalid password")

    user.password = user.generate_hashed_password(args['new_password'])
    db.session.commit()

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })