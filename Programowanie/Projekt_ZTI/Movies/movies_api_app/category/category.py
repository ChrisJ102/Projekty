from flask import jsonify
from webargs.flaskparser import use_args

from movies_api_app import db
from movies_api_app.models import Category, CategorySchema, category_schema
from movies_api_app.utils import validate_json_content_type, get_schema_args, apply_orders, apply_filter, get_pagination, token_required
from movies_api_app.category import category_bp


@category_bp.route('/category', methods=['GET'])
def get_categories():
    query = Category.query
    schema_args = get_schema_args(Category)
    query = apply_orders(Category, query)
    query = apply_filter(Category, query)
    items, pagination = get_pagination(query, 'category.get_categories')
    category = CategorySchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': category,
        'number_of_records': len(category),
        'pagination': pagination
    })


@category_bp.route('/category/<int:category_id>', methods=['GET'])
def get_category(category_id: int):
    category = Category.query.get_or_404(category_id, description=f'Director with id {category_id} not found')
    return jsonify({
        'success': True,
        'data': category_schema.dump(category)
    })


@category_bp.route('/category/<int:category_id>', methods=['PUT'])
@token_required
@validate_json_content_type
@use_args(category_schema, error_status_code=400)
def update_category(user_id: int, args: dict, category_id: int):
    category = Category.query.get_or_404(category_id, description=f'Category with id {category_id} not found')

    category.name = args['name']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': category_schema.dump(category)
    })


@category_bp.route('/category', methods=['POST'])
@token_required
@validate_json_content_type
@use_args(category_schema, error_status_code=400)
def add_category(user_id: int, args: dict):

    category = Category(**args)
    db.session.add(category)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': category_schema.dump(category)
    }), 201


@category_bp.route('/category/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(user_id: int, category_id: int):
    category = Category.query.get_or_404(category_id, description=f'Category with id {category_id} not found')

    db.session.delete(category)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'director with id {category_id} has been deleted'
    })
