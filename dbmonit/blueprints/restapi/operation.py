import logging

from http import HTTPStatus
from flask import Blueprint, abort, request, jsonify
from marshmallow import ValidationError

from dbmonit.models import db, Operation, OperationType, OperationCategory
from dbmonit.schemes import OperationAPISchema, OperationResponseSchema
from dbmonit.annotations import login_required, client_secret_required

operation_blueprint = Blueprint("operations", __name__, url_prefix="/operations")
logger = logging.getLogger(__name__)


@operation_blueprint.route("/", methods=["POST"])
@login_required
def create_operation():
    data = request.json

    if not data:
        logger.error("No input data provided")
        return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST

    try:
        operation_info = OperationAPISchema().load(data)
        logger.debug(operation_info)
    except ValidationError as e:
        logger.error(e.messages)
        return {"error": e.messages}, HTTPStatus.BAD_REQUEST

    operation = Operation(**operation_info)
    db.session.add(operation)
    db.session.commit()

    return {"message": "Operation created", "id": operation.id}


@operation_blueprint.route("/all", methods=["GET"])
@login_required
def get_operations():
    try:
        operations = Operation.query.all()
        schema = OperationResponseSchema(many=True)
        result = schema.dump(operations)
        return jsonify(result), 200
    except Exception:
        abort(404, description="Resource not found")


@operation_blueprint.route("/<int:id>", methods=["GET"])
@login_required
def get_one_operation(id: int):
    try:
        operation = Operation.query.filter_by(id=id).first()
        schema = OperationResponseSchema()
        result = schema.dump(operation)
        return jsonify(result), 200
    except Exception:
        abort(404, description="Resource not found")


@operation_blueprint.route('/trigger', methods=['POST'])
@client_secret_required
def trigger_operation():
    data = request.json

    if not data:
        logger.error("No input data provided")
        return {"message": "No input data provided"}, HTTPStatus.BAD_REQUEST
    
    try:
        operation = Operation.query.filter_by(
            operation_type=data.get('operation'),
            table_name=data.get('table_name'),
        ).first()

        if operation:
            operation.count += 1
            db.session.commit()

            return 'triggered', 200

        category_hash = {
            'SELECT': OperationCategory.READ,
            'UPDATE': OperationCategory.WRITE,
            'INSERT': OperationCategory.WRITE
        }

        new_operation_data = {
            'category': category_hash.get(data.get('operation')).value,
            'operation_type': data.get('operation'),
            'table_name': data.get('table_name')
        }

        operation_info = OperationAPISchema().load(new_operation_data)
        logger.debug(operation_info)

        operation = Operation(**operation_info)
        db.session.add(operation)
        db.session.commit()

        return 'triggered', 200
    
    except Exception as e:
        abort(500, description="A error has ocurred")