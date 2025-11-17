from flask import jsonify
from webargs.flaskparser import use_args

from movies_api_app import db
from movies_api_app.models import PublishingHouse, PublishingHouseSchema, publishing_house_schema
from movies_api_app.utils import validate_json_content_type, get_schema_args, apply_orders, apply_filter, get_pagination, token_required
from movies_api_app.publishing_house import publish_house_bp


@publish_house_bp.route('/publishing_house', methods=['GET'])
def get_publishing_houses():
    query = PublishingHouse.query
    schema_args = get_schema_args(PublishingHouse)
    query = apply_orders(PublishingHouse, query)
    query = apply_filter(PublishingHouse, query)
    items, pagination = get_pagination(query, 'publishing_house.get_publishing_houses')
    publishing_house = PublishingHouseSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': publishing_house,
        'number_of_records': len(publishing_house),
        'pagination': pagination
    })


@publish_house_bp.route('/publishing_house/<int:house_id>', methods=['GET'])
def get_publish_house(house_id: int):
    publish_house = PublishingHouse.query.get_or_404(house_id, description=f'House with id {house_id} not found')
    return jsonify({
        'success': True,
        'data': publishing_house_schema.dump(publish_house)
    })


@publish_house_bp.route('/publishing_house', methods=['POST'])
@token_required
@validate_json_content_type
@use_args(publishing_house_schema, error_status_code=400)
def add_publish_house(user_id: int, args: dict):

    publish_house = PublishingHouse(**args)
    db.session.add(publish_house)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': publishing_house_schema.dump(publish_house)
    }), 201


@publish_house_bp.route('/publishing_house/<int:house_id>', methods=['PUT'])
@token_required
@validate_json_content_type
@use_args(publishing_house_schema, error_status_code=400)
def update_publishing_house(user_id: int, args: dict, house_id: int):
    publish_house = PublishingHouse.query.get_or_404(house_id, description=f'House with id {house_id} not found')

    publish_house.name = args['name']
    publish_house.city = args['city']
    publish_house.post_code = args['post_code']
    publish_house.street = args['street']
    publish_house.email = args['email']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': publishing_house_schema.dump(publish_house)
    })


@publish_house_bp.route('/publishing_house/<int:house_id>', methods=['DELETE'])
@token_required
def delete_publish_house(user_id: int, house_id: int):
    publish_house = PublishingHouse.query.get_or_404(house_id, description=f'House with id {house_id} not found')

    db.session.delete(publish_house)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': f'Publish house with id {house_id} has been deleted'
    })

