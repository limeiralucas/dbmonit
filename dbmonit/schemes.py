from marshmallow import Schema, fields


class OperationAPISchema(Schema):
    operation_type = fields.Str(required=True)
    category = fields.Str()
    table_name = fields.Str()

class OperationResponseSchema(OperationAPISchema):
    id = fields.Str(required=True)
    created_at = fields.DateTime()
