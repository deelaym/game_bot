from marshmallow import Schema, fields


class TimeSchema(Schema):
    seconds = fields.Int()
