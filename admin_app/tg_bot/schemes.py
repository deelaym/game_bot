from marshmallow import Schema, fields


class TimeSchema(Schema):
    session_id = fields.Int()
    seconds = fields.Int()
