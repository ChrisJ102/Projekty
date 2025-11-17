import jwt

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo
from datetime import datetime, date, timedelta
from marshmallow import Schema, fields, validate, validates, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from movies_api_app import db


class Director(db.Model):
    __tablename__ = 'directors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    movies = db.relationship('Movie', back_populates='director', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<{self.__class__.__name__}>: {self.first_name} {self.last_name}'

    @staticmethod
    def additional_validation(param: str, value: str) -> date:
        if param == 'birth_date':
            try:
                value = datetime.strptime(value, '%d-%m-%Y').date()
            except ValueError:
                value = None
        return value


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    loans = db.relationship('Loans', back_populates='user')
    orders = db.relationship('Orders', back_populates='user')

    @staticmethod
    def generate_hashed_password(password: str) -> str:
        return generate_password_hash(password)

    def generate_jwt(self):
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(minutes=current_app.config.get('JWT_EXPIRED_MINUTES', 30))
        }
        return jwt.encode(payload, current_app.config.get('SECRET_KEY'))

    def is_password_valid(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<Name %r>' % self.username


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    movies = db.relationship('Movie', back_populates='category', cascade='all, delete-orphan')

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class PublishingHouse(db.Model):
    __tablename__ = 'publishing_house'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    post_code = db.Column(db.String(6), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    movies = db.relationship('Movie', back_populates='publish_house', cascade='all, delete-orphan')

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    movie_release_year = db.Column(db.BigInteger, nullable=False, unique=True)
    movie_rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    cena = db.Column(db.Integer, nullable=False)
    director_id = db.Column(db.Integer, db.ForeignKey('directors.id'), nullable=False)
    director = db.relationship('Director', back_populates='movies')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', back_populates='movies')
    publish_house_id = db.Column(db.Integer, db.ForeignKey('publishing_house.id'), nullable=False)
    publish_house = db.relationship('PublishingHouse', back_populates='movies')
    loans = db.relationship('Loans', back_populates='movie')
    orders = db.relationship('Orders', back_populates='movie')
    moviesinshop = db.relationship('MoviesInShop', back_populates='movie')

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class Loans(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    movie = db.relationship('Movie', back_populates='loans')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='loans')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=(datetime.utcnow() + timedelta(days=30)))
    price = db.Column(db.Integer, nullable=False)

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    movie = db.relationship('Movie', back_populates='orders')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='orders')
    buy_date = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(255), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    post_code = db.Column(db.String(6), nullable=False)
    moviesinshop = db.relationship('MoviesInShop', back_populates='shop')

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class MoviesInShop(db.Model):
    __tablename__ = 'moviesinshop'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    shop = db.relationship('Shop', back_populates='moviesinshop')
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    movie = db.relationship('Movie', back_populates='moviesinshop')
    how_many = db.Column(db.Integer, nullable=False)

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class DirectorForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    birth_date = DateField("Birth Date", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password1 = PasswordField("Password", validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class MovieForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    movie_release_year = IntegerField("Movie release year", validators=[DataRequired()])
    movie_rating = IntegerField("Movie rating", validators=[DataRequired()])
    description = StringField("Description")
    cena = IntegerField("Price", validators=[DataRequired()])
    director_id = IntegerField("Director", validators=[DataRequired()])
    category_id = IntegerField("Category", validators=[DataRequired()])
    publish_house_id = IntegerField("Publishing House", validators=[DataRequired()])
    submit = SubmitField("Submit")


class FindMovieForm(FlaskForm):
    director = SelectField("Director", validators=[DataRequired()])
    category = SelectField("Category", validators=[DataRequired()])
    publish_house = SelectField("Publish House", validators=[DataRequired()])
    submit = SubmitField("Submit")


class OrderForm(FlaskForm):
    movie_id = IntegerField("Movie", validators=[DataRequired()])
    user_id = IntegerField("User", validators=[DataRequired()])
    shop_id = SelectField("Shop", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ShopForm(FlaskForm):
    city = StringField("City", validators=[DataRequired()])
    street = StringField("Street", validators=[DataRequired()])
    post_code = StringField("Post code", validators=[DataRequired()])
    submit = SubmitField("Submit")


class MovieInShopForm(FlaskForm):
    shop_id = IntegerField("Shop", validators=[DataRequired()])
    movie_id = SelectField("Movie", validators=[DataRequired()])
    how_many = IntegerField("How Many", validators=[DataRequired()])
    submit = SubmitField("Submit")


class DirectorSchema(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True, validate=validate.Length(max=50))
    last_name = fields.String(required=True, validate=validate.Length(max=50))
    birth_date = fields.Date('%d-%m-%Y', required=True)
    movie = fields.List(fields.Nested(lambda: MovieSchema(exclude=['director'])))

    @validates('birth_date')
    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise ValidationError('Birth date must be lower than {datetime.now().date()}')


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(max=255))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))
    creation_date = fields.DateTime(dump_only=True)


class UserPasswordUpdate(Schema):
    current_password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))
    new_password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=255))
    movies = fields.List(fields.Nested(lambda: MovieSchema(only=['title'])))


class PublishingHouseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=255))
    city = fields.String(required=True, validate=validate.Length(max=255))
    post_code = fields.String(required=True, validate=validate.Length(max=6))
    street = fields.String(required=True, validate=validate.Length(max=255))
    email = fields.Email(required=True)
    movies = fields.List(fields.Nested(lambda: MovieSchema(only=['title'])))


class MovieSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(max=50))
    movie_release_year = fields.Integer(required=True)
    movie_rating = fields.Integer(required=True)
    description = fields.String()
    cena = fields.Integer(required=True)
    director_id = fields.Integer(load_only=True)
    director = fields.Nested(lambda: DirectorSchema(only=['id', 'first_name', 'last_name']))
    category_id = fields.Integer(load_only=True, required=True)
    category = fields.Nested(lambda: CategorySchema(only=['name']))
    publish_house_id = fields.Integer(load_only=True, required=True)
    publish_house = fields.Nested(lambda: PublishingHouseSchema(only=['name']))


class LoansSchema(Schema):
    id = fields.Integer(dump_only=True)
    movie_id = fields.Integer(load_only=True, required=True)
    movie = fields.Nested(lambda: MovieSchema(only=['title']))
    user_id = fields.Integer(load_only=True)
    user = fields.Nested(lambda: UserSchema(only=['username']))
    start_date = fields.DateTime(dump_only=True)
    end_date = fields.DateTime(dump_only=True)
    price = fields.Integer(required=True)


class OrdersSchema(Schema):
    id = fields.Integer(dump_only=True)
    movie_id = fields.Integer(load_only=True, required=True)
    movie = fields.Nested(lambda: MovieSchema(only=['title']))
    user_id = fields.Integer(load_only=True, required=True)
    user = fields.Nested(lambda: UserSchema(only=['username']))
    buy_date = fields.DateTime(dump_only=True)


class ShopSchema(Schema):
    id = fields.Integer(dump_only=True)
    city = fields.String(required=True, validate=validate.Length(max=255))
    street = fields.String(required=True, validate=validate.Length(max=255))
    post_code = fields.String(required=True, validate=validate.Length(max=6))
    moviesinshop = fields.List(fields.Nested(lambda: MoviesInShopSchema(only=['how_many', 'movie'])))



class MoviesInShopSchema(Schema):
    id = fields.Integer(dump_only=True)
    movie_id = fields.Integer(load_only=True, required=True)
    movie = fields.Nested(lambda: MovieSchema(only=['title']))
    shop_id = fields.Integer(load_only=True, required=True)
    shop = fields.Nested(lambda: ShopSchema(only=['city']))
    how_many = fields.Integer(required=True)


director_schema = DirectorSchema()
user_schema = UserSchema()
user_password_update_schema = UserPasswordUpdate()
category_schema = CategorySchema()
publishing_house_schema = PublishingHouseSchema()
movie_schema = MovieSchema()
loans_schema = LoansSchema()
order_schema = OrdersSchema()
shop_schema = ShopSchema()
moviesinshops_schema = MoviesInShopSchema()
