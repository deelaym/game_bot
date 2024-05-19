from marshmallow import Schema, fields


class FileIdSchema(Schema):
    file_id = fields.Str(required=True)


class PhotoListSchema(Schema):
    photos = fields.Nested(FileIdSchema, many=True)


class TimeSchema(Schema):
    session_id = fields.Int()
    seconds = fields.Int()
